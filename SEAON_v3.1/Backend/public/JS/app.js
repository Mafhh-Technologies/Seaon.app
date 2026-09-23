document.addEventListener("DOMContentLoaded",()=>{
  if(!Auth.isAuthenticated()){location.href="/app/login.html";return;}

  const user=Auth.user()||{};
  const name=user.full_name||user.email||"SEAON User";
  document.querySelectorAll(".user strong").forEach(x=>x.textContent=name);
  document.querySelectorAll(".user small").forEach(x=>x.textContent=(user.role||"viewer").replace("-"," ").replace(/\b\w/g,c=>c.toUpperCase()));
  const avatar=document.getElementById("userAvatar"); if(avatar) avatar.textContent=name.split(/\s+/).map(x=>x[0]).join("").slice(0,2).toUpperCase();

  const pages=[...document.querySelectorAll(".menu")];
  function showPage(id){
    document.querySelectorAll(".page.content").forEach(p=>p.classList.remove("active-page"));
    const target=document.getElementById(id); if(target) target.classList.add("active-page");
    pages.forEach(a=>a.classList.toggle("active",a.dataset.page===id));
    const loaders={dashboardPage:loadDashboard,inventoryPage:loadInventory,createOrderPage:prepareOrder,bomPage:loadBOM,productionPage:loadProduction,notificationsPage:loadNotifications};
    if(loaders[id]) loaders[id]();
  }
  pages.forEach(a=>a.addEventListener("click",e=>{e.preventDefault();showPage(a.dataset.page);}));
  document.querySelector(".sidebar-close")?.addEventListener("click",()=>document.body.classList.remove("sidebar-open"));
  document.querySelector(".menu-toggle")?.addEventListener("click",()=>document.body.classList.toggle("sidebar-open"));
  document.querySelector(".sidebar-overlay")?.addEventListener("click",()=>document.body.classList.remove("sidebar-open"));
  document.getElementById("topbarBell")?.addEventListener("click",()=>showPage("notificationsPage"));
  document.querySelector(".settings")?.addEventListener("click",e=>{e.preventDefault();toast("Settings are available from the admin panel.","info")});

  document.getElementById("logoutBtn")?.addEventListener("click",()=>Auth.logout());

  function toast(msg,type="info"){
    let c=document.getElementById("toastContainer");
    if(!c){c=document.createElement("div");c.id="toastContainer";c.className="toast-container";document.body.appendChild(c);}
    const el=document.createElement("div"); el.className=`toast ${type}`; el.textContent=msg; c.appendChild(el);
    setTimeout(()=>el.remove(),3500);
  }
  window.Toast={success:m=>toast(m,"success"),error:m=>toast(m,"error"),info:m=>toast(m,"info"),warning:m=>toast(m,"warning")};

  const money=n=>Number(n||0).toLocaleString("en-IN",{maximumFractionDigits:2});
  const esc=x=>String(x??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]));

  async function loadDashboard(){
    try{
      const [orders,inventory,production,low]=await Promise.all([API.orders.list(),API.inventory.list(),API.production.list(),API.inventory.low()]);
      setText("totalOrders",orders.length); setText("pendingProduction",production.filter(x=>x.status==="in-progress").length);
      setText("lowStockAlerts",low.length); setText("completedOrders",orders.filter(x=>x.status==="completed").length);
      const body=document.getElementById("recentOrders");
      if(body) body.innerHTML=orders.slice(0,8).map(o=>`<tr><td>${esc(o.order_number)}</td><td>${esc(o.customer_name)}</td><td>${esc(o.product_name)}</td><td>${money(o.quantity)}</td><td>${esc(o.status)}</td></tr>`).join("")||emptyRow(5);
      setText("inventoryCount",inventory.length);
    }catch(e){toast(e.message,"error")}
  }
  async function loadInventory(){
    try{
      const rows=await API.inventory.list(); const body=document.getElementById("inventoryBody"); if(!body)return;
      body.innerHTML=rows.map(i=>{
        const low=Number(i.quantity)<=Number(i.minimum_stock);
        return `<tr><td>${esc(i.product_name)}</td><td>${esc(i.sku)}</td><td>${money(i.quantity)}</td><td>${esc(i.unit)}</td><td>${money(i.minimum_stock)}</td><td>${esc(i.location)}</td><td><span class="status-badge ${low?"danger":"success"}">${low?"Low Stock":"In Stock"}</span></td><td><button class="btn btn-sm btn-outline" data-adjust="${i.product}">Adjust</button></td></tr>`;
      }).join("")||emptyRow(8);
      setText("inventoryItemCount",rows.length); setText("lowItems",rows.filter(i=>Number(i.quantity)<=Number(i.minimum_stock)).length);
      body.querySelectorAll("[data-adjust]").forEach(b=>b.onclick=async()=>{const v=prompt("Enter stock change (+add / -remove):","0"); if(v===null)return; try{await API.inventory.adjust(b.dataset.adjust,Number(v),"Manual adjustment");toast("Stock updated","success");loadInventory()}catch(e){toast(e.message,"error")}});
    }catch(e){toast(e.message,"error")}
  }
  async function prepareOrder(){
    try{
      const products=await API.products.list(); const sel=document.getElementById("product");
      if(sel) sel.innerHTML='<option value="">Select a product</option>'+products.filter(p=>p.is_active).map(p=>`<option value="${p.id}">${esc(p.name)} (${esc(p.sku)})</option>`).join("");
    }catch(e){toast(e.message,"error")}
  }
  async function createOrder(){
    const customer=document.getElementById("customerName")?.value.trim(), product=document.getElementById("product")?.value, quantity=Number(document.getElementById("quantity")?.value);
    if(!customer||!product||!quantity){toast("Customer, product and quantity are required.","warning");return}
    try{await API.orders.create({customer_name:customer,product:Number(product),quantity,status:"pending"}); toast("Order created successfully","success"); document.getElementById("customerName").value=""; document.getElementById("quantity").value=1; showPage("dashboardPage");}
    catch(e){toast(e.message,"error")}
  }
  async function loadProduction(){
    try{
      const rows=await API.production.list(),body=document.getElementById("productionBody"); if(!body)return;
      body.innerHTML=rows.map(p=>`<tr><td>${esc(p.production_number)}</td><td>${esc(p.customer_name||"-")}</td><td>${esc(p.product_name)}</td><td>${money(p.quantity)}</td><td>-</td><td>${esc(p.status)}</td><td>${money(p.produced_quantity)}/${money(p.quantity)}</td><td>${esc(p.assigned_to||"-")}</td><td>${p.status==="completed"?"-":`<button class="btn btn-sm btn-success" data-complete-production="${p.id}">Complete</button>`}</td></tr>`).join("")||emptyRow(9);
      body.querySelectorAll("[data-complete-production]").forEach(b=>b.onclick=async()=>{try{await API.production.complete(b.dataset.completeProduction);toast("Production completed","success");loadProduction()}catch(e){toast(e.message,"error")}});
    }catch(e){toast(e.message,"error")}
  }
  async function loadBOM(){
    try{
      const rows=await API.bom.list(),box=document.getElementById("bomResults");
      if(box) box.innerHTML=rows.length?`<div class="card"><div class="table-container"><table><thead><tr><th>Product</th><th>Component</th><th>Qty / Unit</th><th>Unit</th><th>Action</th></tr></thead><tbody>${rows.map(x=>`<tr><td>${esc(x.product_name)}</td><td>${esc(x.component_name)}</td><td>${money(x.quantity_per_unit)}</td><td>${esc(x.unit)}</td><td><button class="btn btn-sm btn-danger" data-delete-bom="${x.id}">Delete</button></td></tr>`).join("")}</tbody></table></div></div>`:`<div class="bom-empty"><h3>No BOM Items</h3><p>No bill of materials has been configured yet.</p></div>`;
      box?.querySelectorAll("[data-delete-bom]").forEach(b=>b.onclick=async()=>{if(!confirm("Delete this BOM item?"))return;try{await API.bom.remove(b.dataset.deleteBom);loadBOM()}catch(e){toast(e.message,"error")}});
    }catch(e){toast(e.message,"error")}
  }
  async function loadNotifications(){
    const low=await API.inventory.low().catch(()=>[]);
    setText("stockNotifications",low.length); setText("totalNotifications",low.length); setText("notificationCount",low.length);
    setText("unreadBadge",`${low.length} Unread`);
    const feed=document.getElementById("activityFeed"); if(feed) feed.innerHTML=low.map(x=>`<div class="activity-item"><strong>Low stock: ${esc(x.product_name)}</strong><p>${money(x.quantity)} ${esc(x.unit)} remaining.</p></div>`).join("")||"<p>No active notifications.</p>";
  }
  function setText(id,v){const e=document.getElementById(id);if(e)e.textContent=v}
  function emptyRow(n){return `<tr><td colspan="${n}" style="text-align:center;padding:30px">No records found.</td></tr>`}

  document.getElementById("productForm")?.addEventListener("submit",async e=>{
    e.preventDefault();
    try{
      const name=document.getElementById("productName").value.trim();
      const typeMap={"Raw Material":"raw-material","Semi Finished Product":"component","Finished Product":"finished"};
      const type=typeMap[document.getElementById("productType").value]||document.getElementById("productType").value.toLowerCase().replaceAll(" ","-");
      const data={name,sku:`SKU-${Date.now()}`,product_type:type,unit:document.getElementById("productUnit").value,quantity:Number(document.getElementById("productQuantity").value||0),minimum_stock:Number(document.getElementById("productMinimum").value||0),location:document.getElementById("productLocation").value,thickness:Number(document.getElementById("productThickness").value||0)||null,size:document.getElementById("productSize").value,color:document.getElementById("productColor").value};
      await API.products.create(data); document.getElementById("productModal")?.classList.remove("show"); toast("Product added","success"); loadInventory();
    }catch(e){toast(e.message,"error")}
  });
  document.getElementById("addProductBtn")?.addEventListener("click",()=>document.getElementById("productModal")?.classList.add("show"));
  ["closeProductModal","cancelProduct"].forEach(id=>document.getElementById(id)?.addEventListener("click",()=>document.getElementById("productModal")?.classList.remove("show")));
  document.getElementById("createBtn")?.addEventListener("click",createOrder);
  document.getElementById("cancelBtn")?.addEventListener("click",()=>{document.getElementById("customerName").value="";document.getElementById("quantity").value=1});
  document.getElementById("refreshDashboard")?.addEventListener("click",loadDashboard);
  document.getElementById("markAllRead")?.addEventListener("click",()=>toast("All notifications marked as read","success"));
  document.getElementById("clearNotifications")?.addEventListener("click",()=>{document.getElementById("activityFeed").innerHTML="<p>No active notifications.</p>";toast("Notifications cleared","success")});

  showPage("dashboardPage");
});
