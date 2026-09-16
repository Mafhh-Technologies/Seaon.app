/**
 * Dashboard Module - Displays key metrics and overview
 * Shows statistics, recent orders, and alerts
 */

const Dashboard = {
    /**
     * Initialize dashboard - called when page loads
     */
    init() {
        const content = document.getElementById('contentArea');
        this.render(content);
        this.loadData();
    },
    
    /**
     * Render dashboard HTML
     * @param {HTMLElement} container - Container to render into
     */
    render(container) {
        if (!container) return;
        
        container.innerHTML = `
            <!-- Page Header -->
            <div class="page-header" style="margin-bottom: 24px;">
                <h1 style="font-size: 28px; font-weight: 700;">Dashboard</h1>
                <p style="color: var(--gray-500);">Welcome back! Here's what's happening today.</p>
            </div>
            
            <!-- Stats Cards -->
            <div class="grid grid-4" id="statsGrid">
                <div class="stat-card">
                    <div class="stat-icon blue"><i class="fas fa-shopping-cart"></i></div>
                    <div class="stat-content">
                        <h3 id="totalOrders">0</h3>
                        <p>Total Orders</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon green"><i class="fas fa-boxes"></i></div>
                    <div class="stat-content">
                        <h3 id="totalInventory">0</h3>
                        <p>Inventory Items</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon yellow"><i class="fas fa-industry"></i></div>
                    <div class="stat-content">
                        <h3 id="activeProduction">0</h3>
                        <p>Active Production</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon red"><i class="fas fa-exclamation-triangle"></i></div>
                    <div class="stat-content">
                        <h3 id="lowStockCount">0</h3>
                        <p>Low Stock Alerts</p>
                    </div>
                </div>
            </div>
            
            <!-- Recent Orders & Alerts -->
            <div class="grid grid-2" style="margin-top: 24px;">
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Recent Orders</h3>
                        <button class="btn btn-sm btn-outline" onclick="navigateTo('orders')">
                            View All <i class="fas fa-arrow-right"></i>
                        </button>
                    </div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Order ID</th>
                                    <th>Customer</th>
                                    <th>Product</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody id="recentOrders">
                                <tr><td colspan="4" style="text-align:center; color: var(--gray-400);">Loading...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Inventory Alerts</h3>
                        <button class="btn btn-sm btn-outline" onclick="navigateTo('inventory')">
                            View All <i class="fas fa-arrow-right"></i>
                        </button>
                    </div>
                    <div id="alertsList">
                        <p style="color: var(--gray-400); text-align:center; padding: 20px 0;">Loading alerts...</p>
                    </div>
                </div>
            </div>
            
            <!-- Quick Actions -->
            <div style="margin-top: 24px; display: flex; gap: 12px; flex-wrap: wrap;">
                <button class="btn btn-primary" onclick="showCreateOrderModal()">
                    <i class="fas fa-plus"></i> New Order
                </button>
                <button class="btn btn-success" onclick="showCreateProductionModal()">
                    <i class="fas fa-play"></i> Start Production
                </button>
                <button class="btn btn-outline" onclick="showAddInventoryModal()">
                    <i class="fas fa-plus"></i> Add Inventory
                </button>
            </div>
        `;
    },
    
    /**
     * Load data from API and update dashboard
     */
    async loadData() {
        try {
            // In production, fetch from API
            // const orders = await API.orders.getAll();
            // const inventory = await API.inventory.getAll();
            // const production = await API.production.getAll();
            
            // Using mock data for demo
            const orders = MOCK_DATA.orders;
            const inventory = MOCK_DATA.inventory;
            const production = MOCK_DATA.production;
            
            // Update stats
            document.getElementById('totalOrders').textContent = orders.length;
            document.getElementById('totalInventory').textContent = inventory.length;
            document.getElementById('activeProduction').textContent = 
                production.filter(p => p.status === 'in-progress' || p.status === 'pending').length;
            document.getElementById('lowStockCount').textContent = 
                inventory.filter(item => item.quantity < item.minStock).length;
            
            // Render recent orders (latest 5)
            this.renderRecentOrders(orders.slice(0, 5));
            
            // Render inventory alerts
            this.renderAlerts(inventory);
            
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.showError('Failed to load dashboard data. Please refresh.');
        }
    },
    
    /**
     * Render recent orders in the table
     */
    renderRecentOrders(orders) {
        const tbody = document.getElementById('recentOrders');
        if (!orders || orders.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color: var(--gray-400);">No orders found</td></tr>`;
            return;
        }
        
        tbody.innerHTML = orders.map(order => `
            <tr>
                <td><strong>#${order.id}</strong></td>
                <td>${order.customer}</td>
                <td>${order.product} × ${order.quantity}</td>
                <td><span class="status-badge ${order.status}">${this.capitalize(order.status)}</span></td>
            </tr>
        `).join('');
    },
    
    /**
     * Render inventory alerts (low stock items)
     */
    renderAlerts(inventory) {
        const container = document.getElementById('alertsList');
        const lowStockItems = inventory.filter(item => item.quantity < item.minStock);
        
        if (lowStockItems.length === 0) {
            container.innerHTML = `
                <div style="text-align:center; padding: 20px 0; color: var(--success);">
                    <i class="fas fa-check-circle" style="font-size: 32px; display: block; margin-bottom: 8px;"></i>
                    <p>All inventory levels are healthy!</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = lowStockItems.map(item => `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid var(--gray-100);">
                <div>
                    <strong>${item.name}</strong>
                    <span style="font-size: 12px; color: var(--gray-400); margin-left: 8px;">${item.sku}</span>
                </div>
                <div style="text-align: right;">
                    <span style="color: var(--danger); font-weight: 600;">${item.quantity} ${item.unit}</span>
                    <span style="font-size: 12px; color: var(--gray-400); display: block;">Min: ${item.minStock} ${item.unit}</span>
                </div>
            </div>
        `).join('');
    },
    
    /**
     * Show error message in dashboard
     */
    showError(message) {
        const container = document.getElementById('contentArea');
        const errorEl = document.createElement('div');
        errorEl.style.cssText = `
            background: #FEF2F2;
            border: 1px solid #FECACA;
            border-radius: 8px;
            padding: 16px 20px;
            color: var(--danger);
            margin-top: 16px;
        `;
        errorEl.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
        container.appendChild(errorEl);
    },
    
    /**
     * Utility: Capitalize first letter
     */
    capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
};

// ========================================
// MODAL TRIGGERS (to be implemented in respective modules)
// ========================================

function showCreateOrderModal() {
    // Delegate to Orders module
    if (typeof Orders !== 'undefined' && Orders.showCreateModal) {
        Orders.showCreateModal();
    } else {
        alert('Order creation modal will be implemented in orders.js');
    }
}

function showCreateProductionModal() {
    if (typeof Production !== 'undefined' && Production.showCreateModal) {
        Production.showCreateModal();
    } else {
        alert('Production creation modal will be implemented in production.js');
    }
}

function showAddInventoryModal() {
    if (typeof Inventory !== 'undefined' && Inventory.showCreateModal) {
        Inventory.showCreateModal();
    } else {
        alert('Inventory addition modal will be implemented in inventory.js');
    }
}