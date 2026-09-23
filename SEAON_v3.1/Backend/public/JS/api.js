window.API = {
  async request(path, options={}) {
    const token=localStorage.getItem("seaon_access_token");
    const headers={"Content-Type":"application/json",...(options.headers||{})};
    if(token) headers.Authorization=`Bearer ${token}`;
    const res=await fetch(`/api${path}`,{...options,headers});
    const text=await res.text();
    let data={}; try { data=text?JSON.parse(text):{} } catch { data={detail:text}; }
    if(res.status===401 && token) {
      const refresh=localStorage.getItem("seaon_refresh_token");
      if(refresh) {
        const rr=await fetch("/api/auth/refresh/",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({refresh})});
        if(rr.ok){ const r=await rr.json(); localStorage.setItem("seaon_access_token",r.access); return this.request(path,options); }
      }
      localStorage.removeItem("seaon_access_token"); localStorage.removeItem("seaon_refresh_token"); localStorage.removeItem("seaon_user");
    }
    if(!res.ok) throw new Error(data.detail || data.message || `Request failed (${res.status})`);
    return data;
  },
  auth:{
    login:(email,password)=>API.request("/auth/login/",{method:"POST",body:JSON.stringify({email,password})}),
    me:()=>API.request("/auth/me/"),
    logout:()=>API.request("/auth/logout/",{method:"POST"})
  },
  products:{
    list:()=>API.request("/products/"), create:data=>API.request("/products/",{method:"POST",body:JSON.stringify(data)})
  },
  inventory:{
    list:()=>API.request("/inventory/"), low:()=>API.request("/inventory/low_stock/"),
    adjust:(productId,delta,note="")=>API.request(`/inventory/${productId}/stock/`,{method:"PATCH",body:JSON.stringify({delta,note})})
  },
  orders:{
    list:()=>API.request("/orders/"), create:data=>API.request("/orders/",{method:"POST",body:JSON.stringify(data)}),
    complete:id=>API.request(`/orders/${id}/complete/`,{method:"PATCH"})
  },
  production:{
    list:()=>API.request("/production/"), create:data=>API.request("/production/",{method:"POST",body:JSON.stringify(data)}),
    complete:id=>API.request(`/production/${id}/complete/`,{method:"POST"})
  },
  bom:{
    list:()=>API.request("/bom/"), create:data=>API.request("/bom/",{method:"POST"}), remove:id=>API.request(`/bom/${id}/`,{method:"DELETE"})
  }
};
