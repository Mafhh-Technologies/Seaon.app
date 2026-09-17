/**
 * API Layer - Handles all HTTP requests to the backend
 * Centralized error handling, request/response interceptors
 */

const API = {
    // Base URL - change this to your actual backend
    // baseURL: 'http://localhost:3000/api',
    baseURL: 'http://localhost:8000/api',
    
    // Default headers
    headers: {
        'Content-Type': 'application/json',
    },
    
    /**
     * Get auth token from localStorage
     */
    getToken() {
        return localStorage.getItem('auth_token');
    },
    
    /**
     * Set auth token in headers
     */
    setAuthHeader() {
        const token = this.getToken();
        if (token) {
            this.headers['Authorization'] = `Bearer ${token}`;
        }
        return this.headers;
    },
    
    /**
     * Generic request handler
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.headers,
                ...options.headers,
            },
        };
        
        // Add auth token if available
        const token = this.getToken();
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        
        try {
            const response = await fetch(url, config);
            
            // Handle non-OK responses
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            // Parse JSON response
            const data = await response.json();
            return data;
            
        } catch (error) {
            console.error('API Request Failed:', error);
            throw error;
        }
    },
    
    // ========================================
    // AUTH ENDPOINTS
    // ========================================
    auth: {
        /**
         * Login user
         * @param {string} email - User email
         * @param {string} password - User password
         * @returns {Promise<Object>} User data with token
         */
        async login(email, password) {
            return API.request('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, password }),
            });
        },
        
        /**
         * Logout user
         */
        async logout() {
            return API.request('/auth/logout', {
                method: 'POST',
            });
        },
        
        /**
         * Get current user profile
         */
        async me() {
            return API.request('/auth/me');
        },
    },
    
    // ========================================
    // ORDERS ENDPOINTS
    // ========================================
    orders: {
        /**
         * Get all orders with pagination
         * @param {number} page - Page number
         * @param {number} limit - Items per page
         */
        async getAll(page = 1, limit = 20) {
            return API.request(`/orders?page=${page}&limit=${limit}`);
        },
        
        /**
         * Get single order by ID
         */
        async getById(id) {
            return API.request(`/orders/${id}`);
        },
        
        /**
         * Create new order
         */
        async create(orderData) {
            return API.request('/orders', {
                method: 'POST',
                body: JSON.stringify(orderData),
            });
        },
        
        /**
         * Update order status
         */
        async updateStatus(id, status) {
            return API.request(`/orders/${id}/status`, {
                method: 'PATCH',
                body: JSON.stringify({ status }),
            });
        },
        
        /**
         * Delete order
         */
        async delete(id) {
            return API.request(`/orders/${id}`, {
                method: 'DELETE',
            });
        },
    },
    
    // ========================================
    // INVENTORY ENDPOINTS
    // ========================================
    inventory: {
        /**
         * Get all inventory items
         */
        async getAll() {
            return API.request('/inventory');
        },
        
        /**
         * Get low stock items
         */
        async getLowStock(threshold = 10) {
            return API.request(`/inventory/low-stock?threshold=${threshold}`);
        },
        
        /**
         * Update stock quantity
         */
        async updateStock(id, quantity) {
            return API.request(`/inventory/${id}/stock`, {
                method: 'PATCH',
                body: JSON.stringify({ quantity }),
            });
        },
        
        /**
         * Add new inventory item
         */
        async create(itemData) {
            return API.request('/inventory', {
                method: 'POST',
                body: JSON.stringify(itemData),
            });
        },
    },
    
    // ========================================
    // PRODUCTION ENDPOINTS
    // ========================================
    production: {
        /**
         * Get all production jobs
         */
        async getAll() {
            return API.request('/production');
        },
        
        /**
         * Start a production job
         */
        async startJob(jobData) {
            return API.request('/production/start', {
                method: 'POST',
                body: JSON.stringify(jobData),
            });
        },
        
        /**
         * Complete a production job
         */
        async completeJob(id, output) {
            return API.request(`/production/${id}/complete`, {
                method: 'POST',
                body: JSON.stringify({ output }),
            });
        },
    },
    
    // ========================================
    // BOM (Bill of Materials) ENDPOINTS
    // ========================================
    bom: {
        /**
         * Get all BOM items
         */
        async getAll() {
            return API.request('/bom');
        },
        
        /**
         * Get BOM for a specific product
         */
        async getByProduct(productId) {
            return API.request(`/bom/product/${productId}`);
        },
        
        /**
         * Create new BOM entry
         */
        async create(bomData) {
            return API.request('/bom', {
                method: 'POST',
                body: JSON.stringify(bomData),
            });
        },
    },
};

// ========================================
// MOCK DATA (for demo without backend)
// ========================================
const MOCK_DATA = {
    // Mock orders
    orders: [
        { id: 1, customer: 'Acme Corp', product: 'Widget A', quantity: 50, status: 'pending', date: '2026-09-01' },
        { id: 2, customer: 'TechStart Inc', product: 'Widget B', quantity: 30, status: 'completed', date: '2026-08-28' },
        { id: 3, customer: 'GreenLeaf Ltd', product: 'Widget C', quantity: 100, status: 'in-progress', date: '2026-09-03' },
        { id: 4, customer: 'BlueSky Co', product: 'Widget A', quantity: 25, status: 'pending', date: '2026-09-05' },
        { id: 5, customer: 'RedRocket Corp', product: 'Widget B', quantity: 75, status: 'cancelled', date: '2026-08-25' },
    ],
    
    // Mock inventory
    inventory: [
        { id: 1, name: 'Raw Material X', sku: 'RM-001', quantity: 500, minStock: 50, unit: 'kg' },
        { id: 2, name: 'Raw Material Y', sku: 'RM-002', quantity: 120, minStock: 30, unit: 'kg' },
        { id: 3, name: 'Component A', sku: 'CMP-001', quantity: 250, minStock: 20, unit: 'pcs' },
        { id: 4, name: 'Component B', sku: 'CMP-002', quantity: 45, minStock: 50, unit: 'pcs' }, // Low stock!
        { id: 5, name: 'Finished Product Z', sku: 'FP-001', quantity: 80, minStock: 10, unit: 'pcs' },
    ],
    
    // Mock production jobs
    production: [
        { id: 1, product: 'Widget A', quantity: 50, status: 'in-progress', startDate: '2026-09-03', operator: 'Jane Smith' },
        { id: 2, product: 'Widget B', quantity: 30, status: 'completed', startDate: '2026-08-30', operator: 'John Doe' },
        { id: 3, product: 'Widget C', quantity: 100, status: 'pending', startDate: '2026-09-06', operator: 'Unassigned' },
    ],
    
    // Mock BOM
    bom: [
        { id: 1, product: 'Widget A', component: 'Raw Material X', quantity: 2, unit: 'kg' },
        { id: 2, product: 'Widget A', component: 'Component A', quantity: 4, unit: 'pcs' },
        { id: 3, product: 'Widget B', component: 'Raw Material Y', quantity: 3, unit: 'kg' },
        { id: 4, product: 'Widget B', component: 'Component B', quantity: 2, unit: 'pcs' },
        { id: 5, product: 'Widget C', component: 'Raw Material X', quantity: 1, unit: 'kg' },
        { id: 6, product: 'Widget C', component: 'Component A', quantity: 6, unit: 'pcs' },
    ],
};