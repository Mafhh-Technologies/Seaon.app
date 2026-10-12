/*
 * SEAON ERP API client.
 *
 * All browser requests go through this object so authentication, response
 * parsing and error handling stay in one place.
 */
const API = {
  async request(path, options = {}) {
    let token = localStorage.getItem("seaon_access_token");
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    };

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`/api${path}`, {
      ...options,
      headers,
    });

    const raw = await response.text();
    let data = {};

    try {
      data = raw ? JSON.parse(raw) : {};
    } catch {
      // Never put Django's full HTML debug page into the ERP error box.
      const titleMatch = raw.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
      const title = titleMatch
        ? titleMatch[1].replace(/<[^>]+>/g, "").trim()
        : "";

      data = {
        detail: title || `Request failed (${response.status})`,
      };
    }

    // Refresh an expired access token once.
    if (response.status === 401 && token && !options._retried) {
      const refresh = localStorage.getItem("seaon_refresh_token");

      if (refresh) {
        const refreshResponse = await fetch("/api/auth/refresh/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh }),
        });

        if (refreshResponse.ok) {
          const refreshed = await refreshResponse.json();
          localStorage.setItem("seaon_access_token", refreshed.access);
          return API.request(path, { ...options, _retried: true });
        }
      }

      localStorage.removeItem("seaon_access_token");
      localStorage.removeItem("seaon_refresh_token");
      localStorage.removeItem("seaon_user");
      location.href = "/app/login.html";
      throw new Error("Your session has expired.");
    }

    if (!response.ok) {
      throw new Error(
        data.detail || data.message || `Request failed (${response.status})`
      );
    }

    return data;
  },

  auth: {
    login: (email, password) =>
      API.request("/auth/login/", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }),

    me: () => API.request("/auth/me/"),

    logout: () =>
      API.request("/auth/logout/", {
        method: "POST",
      }),
  },

  dashboard: () => API.request("/dashboard/"),

  products: {
    list: () => API.request("/products/"),
    create: (data) =>
      API.request("/products/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
  },

  inventory: {
    list: () => API.request("/inventory/"),
    low: () => API.request("/inventory/low_stock/"),
    adjust: (id, delta, note) =>
      API.request(`/inventory/${id}/stock/`, {
        method: "PATCH",
        body: JSON.stringify({ delta, note }),
      }),
    batches: () => API.request("/inventory/batches/"),
    receive: (data) =>
      API.request("/inventory/batches/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    consume: (data) =>
      API.request("/inventory/fifo/consume/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
  },

  orders: {
    list: () => API.request("/orders/"),
    create: (data) =>
      API.request("/orders/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    complete: (id) =>
      API.request(`/orders/${id}/complete/`, {
        method: "PATCH",
      }),
  },

  production: {
    list: () => API.request("/production/"),
    create: (data) =>
      API.request("/production/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    complete: (id) =>
      API.request(`/production/${id}/complete/`, {
        method: "POST",
      }),
  },

  bom: {
    list: () => API.request("/bom/"),
    create: (data) =>
      API.request("/bom/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    remove: (id) =>
      API.request(`/bom/${id}/`, {
        method: "DELETE",
      }),
  },

  warehouse: {
    list: () => API.request("/warehouse/"),
    create: (data) =>
      API.request("/warehouse/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
  },

  returns: {
    list: () => API.request("/returns/"),
    create: (data) =>
      API.request("/returns/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    update: (id, data) =>
      API.request(`/returns/${id}/`, {
        method: "PATCH",
        body: JSON.stringify(data),
      }),
  },

  reports: () => API.request("/reports/"),
};

// Expose the client to the other browser scripts.
window.API = API;
