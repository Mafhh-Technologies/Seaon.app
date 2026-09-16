/**
 * Orders Module - Manages customer orders
 * CRUD operations, status updates, and order tracking
 */

const Orders = {
    /**
     * Current orders data
     */
    orders: [],
    
    /**
     * Render orders page
     * @param {HTMLElement} container - Container to render into
     */
    render(container) {
        if (!container) return;
        
        container.innerHTML = `
            <div class="page-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px;">
                <div>
                    <h1 style="font-size: 28px; font-weight: 700;">Orders</h1>
                    <p style="color: var(--gray-500);">Manage and track all customer orders</p>
                </div>
                <button class="btn btn-primary" onclick="Orders.showCreateModal()">
                    <i class="fas fa-plus"></i> New Order
                </button>
            </div>
            
            <!-- Filters -->
            <div style="display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap;">
                <select id="orderStatusFilter" style="padding: 8px 14px; border-radius: 6px; border: 1px solid var(--gray-200); background: white;">
                    <option value="all">All Status</option>
                    <option value="pending">Pending</option>
                    <option value="in-progress">In Progress</option>
                    <option value="completed">Completed</option>
                    <option value="cancelled">Cancelled</option>
                </select>
                <input type="text" id="orderSearch" placeholder="Search orders..." style="padding: 8px 14px; border-radius: 6px; border: 1px solid var(--gray-200); flex: 1; min-width: 200px;">
                <button class="btn btn-sm btn-outline" onclick="Orders.loadData()">
                    <i class="fas fa-refresh"></i> Refresh
                </button>
            </div>
            
            <!-- Orders Table -->
            <div class="card">
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Order ID</th>
                                <th>Customer</th>
                                <th>Product</th>
                                <th>Quantity</th>
                                <th>Date</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="ordersTableBody">
                            <tr><td colspan="7" style="text-align:center; padding: 40px; color: var(--gray-400);">
                                <i class="fas fa-spinner fa-spin"></i> Loading orders...
                            </td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Pagination -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 16px; flex-wrap: wrap; gap: 8px;">
                <span id="orderCount" style="color: var(--gray-500); font-size: 14px;">0 orders</span>
                <div id="orderPagination" style="display: flex; gap: 6px;"></div>
            </div>
        `;
        
        // Setup event listeners
        document.getElementById('orderStatusFilter')?.addEventListener('change', () => this.loadData());
        document.getElementById('orderSearch')?.addEventListener('input', () => this.loadData());
        
        // Load data
        this.loadData();
    },
    
    /**
     * Load orders from API
     */
    async loadData() {
        try {
            // In production: const data = await API.orders.getAll();
            // Using mock data
            let orders = [...MOCK_DATA.orders];
            
            // Apply filters
            const statusFilter = document.getElementById('orderStatusFilter')?.value;
            const searchQuery = document.getElementById('orderSearch')?.value?.toLowerCase();
            
            if (statusFilter && statusFilter !== 'all') {
                orders = orders.filter(o => o.status === statusFilter);
            }
            
            if (searchQuery) {
                orders = orders.filter(o => 
                    o.customer.toLowerCase().includes(searchQuery) ||
                    o.product.toLowerCase().includes(searchQuery) ||
                    o.id.toString().includes(searchQuery)
                );
            }
            
            this.orders = orders;
            this.renderTable(orders);
            this.updatePagination(orders.length);
            
        } catch (error) {
            console.error('Failed to load orders:', error);
            document.getElementById('ordersTableBody').innerHTML = `
                <tr><td colspan="7" style="text-align:center; padding: 40px; color: var(--danger);">
                    <i class="fas fa-exclamation-circle"></i> Failed to load orders. Please try again.
                </td></tr>
            `;
        }
    },
    
    /**
     * Render orders table
     */
    renderTable(orders) {
        const tbody = document.getElementById('ordersTableBody');
        if (!tbody) return;
        
        if (orders.length === 0) {
            tbody.innerHTML = `
                <tr><td colspan="7" style="text-align:center; padding: 60px 20px; color: var(--gray-400);">
                    <i class="fas fa-inbox" style="font-size: 36px; display: block; margin-bottom: 12px;"></i>
                    No orders found
                </td></tr>
            `;
            return;
        }
        
        tbody.innerHTML = orders.map(order => `
            <tr>
                <td><strong>#${order.id}</strong></td>
                <td>${order.customer}</td>
                <td>${order.product}</td>
                <td>${order.quantity}</td>
                <td>${this.formatDate(order.date)}</td>
                <td>
                    <span class="status-badge ${order.status}">${this.capitalize(order.status)}</span>
                </td>
                <td>
                    <div style="display: flex; gap: 6px;">
                        <button class="btn btn-sm btn-outline" onclick="Orders.updateStatus(${order.id}, 'completed')" title="Complete">
                            <i class="fas fa-check"></i>
                        </button>
                        <button class="btn btn-sm btn-outline" onclick="Orders.updateStatus(${order.id}, 'cancelled')" title="Cancel">
                            <i class="fas fa-times"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="Orders.deleteOrder(${order.id})" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    },
    
    /**
     * Update order status
     */
    async updateStatus(orderId, newStatus) {
        if (!confirm(`Update order #${orderId} status to "${newStatus}"?`)) return;
        
        try {
            // In production: await API.orders.updateStatus(orderId, newStatus);
            
            // Mock update
            const order = MOCK_DATA.orders.find(o => o.id === orderId);
            if (order) {
                order.status = newStatus;
                this.loadData(); // Refresh table
                this.showToast(`Order #${orderId} updated to ${newStatus}`, 'success');
            }
        } catch (error) {
            console.error('Failed to update order:', error);
            this.showToast('Failed to update order status', 'error');
        }
    },
    
    /**
     * Delete order
     */
    async deleteOrder(orderId) {
        if (!confirm(`Delete order #${orderId}? This action cannot be undone.`)) return;
        
        try {
            // In production: await API.orders.delete(orderId);
            
            // Mock delete
            const index = MOCK_DATA.orders.findIndex(o => o.id === orderId);
            if (index > -1) {
                MOCK_DATA.orders.splice(index, 1);
                this.loadData(); // Refresh table
                this.showToast(`Order #${orderId} deleted successfully`, 'success');
            }
        } catch (error) {
            console.error('Failed to delete order:', error);
            this.showToast('Failed to delete order', 'error');
        }
    },
    
    /**
     * Show create order modal
     */
    showCreateModal() {
        // Create modal overlay if it doesn't exist
        let modal = document.getElementById('orderModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'orderModal';
            modal.className = 'modal-overlay';
            document.body.appendChild(modal);
        }
        
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3><i class="fas fa-plus-circle" style="color: var(--primary);"></i> Create New Order</h3>
                    <button class="modal-close" onclick="document.getElementById('orderModal').classList.remove('active')">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <form id="createOrderForm" onsubmit="Orders.createOrder(event)">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Customer Name *</label>
                            <input type="text" id="orderCustomer" required placeholder="e.g., Acme Corp" />
                        </div>
                        <div class="form-group">
                            <label>Product *</label>
                            <select id="orderProduct" required>
                                <option value="">Select Product</option>
                                <option value="Widget A">Widget A</option>
                                <option value="Widget B">Widget B</option>
                                <option value="Widget C">Widget C</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Quantity *</label>
                            <input type="number" id="orderQuantity" required min="1" placeholder="e.g., 50" />
                        </div>
                        <div class="form-group">
                            <label>Status</label>
                            <select id="orderStatus">
                                <option value="pending">Pending</option>
                                <option value="in-progress">In Progress</option>
                                <option value="completed">Completed</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Notes</label>
                        <textarea id="orderNotes" placeholder="Additional notes..." rows="2"></textarea>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline" onclick="document.getElementById('orderModal').classList.remove('active')">
                            Cancel
                        </button>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-save"></i> Create Order
                        </button>
                    </div>
                </form>
            </div>
        `;
        
        modal.classList.add('active');
    },
    
    /**
     * Create new order
     */
    async createOrder(event) {
        event.preventDefault();
        
        const customer = document.getElementById('orderCustomer').value.trim();
        const product = document.getElementById('orderProduct').value;
        const quantity = parseInt(document.getElementById('orderQuantity').value);
        const status = document.getElementById('orderStatus').value;
        const notes = document.getElementById('orderNotes').value.trim();
        
        if (!customer || !product || !quantity) {
            this.showToast('Please fill all required fields', 'error');
            return;
        }
        
        try {
            // In production: await API.orders.create({ customer, product, quantity, status, notes });
            
            // Mock create
            const newOrder = {
                id: MOCK_DATA.orders.length + 1,
                customer,
                product,
                quantity,
                status,
                date: new Date().toISOString().split('T')[0],
                notes,
            };
            MOCK_DATA.orders.unshift(newOrder);
            
            // Close modal and refresh
            document.getElementById('orderModal').classList.remove('active');
            this.loadData();
            this.showToast(`Order #${newOrder.id} created successfully!`, 'success');
            
        } catch (error) {
            console.error('Failed to create order:', error);
            this.showToast('Failed to create order', 'error');
        }
    },
    
    /**
     * Update pagination info
     */
    updatePagination(total) {
        const countEl = document.getElementById('orderCount');
        if (countEl) {
            countEl.textContent = `${total} order${total !== 1 ? 's' : ''}`;
        }
    },
    
    /**
     * Format date for display
     */
    formatDate(dateStr) {
        if (!dateStr) return '-';
        const d = new Date(dateStr);
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    },
    
    /**
     * Capitalize first letter
     */
    capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    },
    
    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        
        // Auto-remove after 4 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
};