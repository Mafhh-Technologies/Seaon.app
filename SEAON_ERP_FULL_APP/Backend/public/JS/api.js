/* API CLIENT
   Every browser request goes through this file.
   That makes the frontend easy to maintain: UI code calls API.products.list()
   instead of repeating fetch(), headers and error handling everywhere.
*/
window.API={
  async request(path,options={}){
    let token=localStorage.getItem("seaon_access_token");
    const headers={"Content-Type":"application/json",...(options.headers||{})};
    if(token) headers.Authorization=`Bearer ${token}`;
    let response=await fetch(`/api${path}`,{...options,headers});
    let raw=await response.text(), data={};
    try{data=raw?JSON.parse(raw):{}}catch{data={detail:raw};}

    // Automatically renew the access token once when it expires.
    if(response.status===401 && token && !options._retried){
      const refresh=localStorage.getItem("seaon_refresh_token");
      if(refresh){
        const rr=await fetch("/api/auth/refresh/",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({refresh})});
        if(rr.ok){
          const r=await rr.json();
          localStorage.setItem("seaon_access_token",r.access);
          return this.request(path,{...options,_retried:true});
        }
      }
      localStorage.clear();
      location.href="/app/login.html";
      throw new Error("Your session has expired.");
    }
    if(!response.ok) throw new Error(data.detail||data.message||`Request failed (${response.status})`);
    return data;
  },
  auth:{
    login:(email,password)=>API.request("/auth/login/",{method:"POST",body:JSON.stringify({email,password})}),
    me:()=>API.request("/auth/me/"),
    logout:()=>API.request("/auth/logout/",{method:"POST"})
  },
  dashboard:()=>this.request("/dashboard/"),
  products:{
    list:()=>this.request("/products/"),
    create:data=>this.request("/products/",{method:"POST",body:JSON.stringify(data)})
  },
  inventory:{
    list:()=>this.request("/inventory/"),
    low:()=>this.request("/inventory/low_stock/"),
    adjust:(id,delta,note)=>this.request(`/inventory/${id}/stock/`,{method:"PATCH",body:JSON.stringify({delta,note})}),
    batches:()=>this.request("/inventory/batches/"),
    receive:data=>this.request("/inventory/batches/",{method:"POST",body:JSON.stringify(data)}),
    consume:data=>this.request("/inventory/fifo/consume/",{method:"POST",body:JSON.stringify(data)})
  },
  orders:{
    list:()=>this.request("/orders/"),
    create:data=>this.request("/orders/",{method:"POST",body:JSON.stringify(data)}),
    complete:id=>this.request(`/orders/${id}/complete/`,{method:"PATCH"})
  },
  production:{
    list:()=>this.request("/production/"),
    create:data=>this.request("/production/",{method:"POST",body:JSON.stringify(data)}),
    complete:id=>this.request(`/production/${id}/complete/`,{method:"POST"})
  },
  bom:{
    list:()=>this.request("/bom/"),
    create:data=>this.request("/bom/",{method:"POST",body:JSON.stringify(data)}),
    remove:id=>this.request(`/bom/${id}/`,{method:"DELETE"})
  },
  warehouse:{
    list:()=>this.request("/warehouse/"),
    create:data=>this.request("/warehouse/",{method:"POST",body:JSON.stringify(data)})
  },
  returns:{
    list:()=>this.request("/returns/"),
    create:data=>this.request("/returns/",{method:"POST",body:JSON.stringify(data)}),
    update:(id,data)=>this.request(`/returns/${id}/`,{method:"PATCH",body:JSON.stringify(data)})
  },
  reports:()=>this.request("/reports/")
};
