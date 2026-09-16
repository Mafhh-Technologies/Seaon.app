/**
 * Inventory Module - Manages inventory items
 * Stock tracking, low stock alerts, and inventory adjustments
 */

const Inventory = {
    /**
     * Current inventory data
     */
    items: [],
    
    /**
     * Render inventory page
     */
    render(container) {
        if (!container) return;
        
        container.innerHTML = `
            <div class="page-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px;">
                <div>
                    <h1 style="font-size: 28px; font-weight: 700;">Inventory</h1>
                    <p style="color: var(--gray-500);">Manage your stock and materials</p>
                </div>
                <button class="btn btn-primary" onclick="Inventory.showCreateModal()">
                    <i class="fas fa-plus"></i> Add Item
                </button>
            </div>
            
            <!-- Quick Stats -->
            <div class="grid grid-3" style="margin-bottom: 20px;">
                <div class="stat-card" style="border-left: 4px solid var(--primary);">
                    <div class="stat-content">
                        <h3 id="totalItems">0</h3>
                        <p>Total Items</p>
                    </div>
                </div>
                <div class="stat-card" style="border-left: 4px solid var(--success);">
                    <div class="stat-content">
                        <h3 id="totalValue">0</h3>
                        <p>Total Stock Value</p>
                    </div>
                </div>
                <div class="stat-card" style="border-left: 4px solid var(--danger);">
                    <div class="stat-content">
                        <h3 id="lowItems">0</h3>
                        <p>Low Stock Items</p>
                    </div>
                </div>
            </div>
            
            <!-- Filters -->
            <div style="display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap;">
                <input type="text" id="inventorySearch" placeholder="Search items by name or SKU..." style="padding: 8px 14px; border-radius: 6px; border: 1px solid var(--gray-200); flex: 1; min-width: 200px;">
                <select id="inventoryFilter" style="padding: 8px 14px; border-radius: 6px; border: 1px solid var(--gray-200); background: white;">
                    <option value="all">All Items</option>
                    <option value="low">Low Stock</option>
                    <option value="in-stock">In Stock</option>
                </select>
                <button class="btn btn-sm btn-outline" onclick="Inventory.loadData()">
                    <i class="fas fa-refresh"></i> Refresh
                </button>
            </div>
            
            <!-- Inventory Table -->
            <div class="card">
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>SKU</th>
                                <th>Quantity</th>
                                <th>Min. Stock</th>
                                <th>Unit</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="inventoryTableBody">
                            <tr><td colspan="7" style="text-align:center; padding: 40px; color: var(--gray-400);">
                                <i class="fas fa-spinner fa-spin"></i> Loading inventory...
                            </td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        // Setup event listeners
        document.getElementById('inventorySearch')?.addEventListener('input', () => this.loadData());
        document.getElementById('inventoryFilter')?.addEventListener('change', () => this.loadData());
        
        this.loadData();
    },
    
    /**
     * Load inventory data
     */
    async loadData() {
        try {
            // In production: const data = await API.inventory.getAll();
            let items = [...MOCK_DATA.inventory];
            
            // Apply filters
            const searchQuery = document.getElementById('inventorySearch')?.value?.toLowerCase();
            const filter = document.getElementById('inventoryFilter')?.value;
            
            if (searchQuery) {
                items = items.filter(item => 
                    item.name.toLowerCase().includes(searchQuery) ||
                    item.sku.toLowerCase().includes(searchQuery)
                );
            }
            
            if (filter === 'low') {
                items = items.filter(item => item.quantity < item.minStock);
            } else if (filter === 'in-stock') {
                items = items.filter(item => item.quantity >= item.minStock);
            }
            
            this.items = items;
            this.renderTable(items);
            this.updateStats(items);
            
        } catch (error) {
            console.error('Failed to load inventory:', error);
            document.getElementById('inventoryTableBody').innerHTML = `
                <tr><td colspan="7" style="text-align:center; padding: 40px; color: var(--danger);">
                    <i class="fas fa-exclamation-circle"></i> Failed to load inventory
                </td></tr>
            `;
        }
    },
    
    /**
     * Render inventory table
     */
    renderTable(items) {
        const tbody = document.getElementById('inventoryTableBody');
        if (!tbody) return;
        
        if (items.length === 0) {
            tbody.innerHTML = `
                <tr><td colspan="7" style="text-align:center; padding: 60px 20px; color: var(--gray-400);">
                    <i class="fas fa-box-open" style="font-size: 36px; display: block; margin-bottom: 12px;"></i>
                    No inventory items found
                </td></tr>
            `;
            return;
        }
        
        tbody.innerHTML = items.map(item => {
            const isLow = item.quantity < item.minStock;
            return `
                <tr>
                    <td><strong>${item.name}</strong></td>
                    <td><span style="font-size: 12px; color: var(--gray-400);">${item.sku}</span></td>
                    <td style="font-weight: ${isLow ? '700' : '400'}; color: ${isLow ? 'var(--danger)' : 'inherit'};">
                        ${item.quantity}
                    </td>
                    <td>${item.minStock}</td>
                    <td>${item.unit}</td>
                    <td>
                        <span class="status-badge ${isLow ? 'cancelled' : 'completed'}">
                            ${isLow ? '⚠️ Low Stock' : 'In Stock'}
                        </span>
                    </td>
                    <td>
                        <div style="display: flex; gap: 6px;">
                            <button class="btn btn-sm btn-success" onclick="Inventory.adjustStock(${item.id}, 10)" title="Add Stock">
                                <i class="fas fa-plus"></i>
                            </button>
                            <button class="btn btn-sm btn-outline" onclick="Inventory.adjustStock(${item.id}, -5)" title="Remove Stock">
                                <i class="fas fa-minus"></i>
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="Inventory.deleteItem(${item.id})" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    },
    
    /**
     * Update stats cards
     */
    updateStats(items) {
        document.getElementById('totalItems').textContent = items.length;
        document.getElementById('lowItems').textContent = items.filter(i => i.quantity < i.minStock).length;
        
        // Mock total value calculation (in real app, add price field)
        const totalValue = items.reduce((sum, item) => sum + (item.quantity * 10), 0);
        document.getElementById('totalValue').textContent = `$${totalValue.toLocaleString()}`;
    },
    
    /**
     * Adjust stock quantity
     */
    async adjustStock(itemId, change) {
        try {
            // In production: await API.inventory.updateStock(itemId, change);
            
            const item = MOCK_DATA.inventory.find(i => i.id === itemId);
            if (!item) return;
            
            const newQuantity = Math.max(0, item.quantity + change);
            item.quantity = newQuantity;
            
            this.loadData(); // Refresh table
            this.showToast(`Stock updated: ${item.name} is now ${newQuantity} ${item.unit}`, 'success');
            
        } catch (error) {
            console.error('Failed to adjust stock:', error);
            this.showToast('Failed to update stock', 'error');
        }
    },
    
    /**
     * Delete inventory item
     */
    async deleteItem(itemId) {
        if (!confirm('Delete this inventory item? This action cannot be undone.')) return;
        
        try {
            // In production: await API.inventory.delete(itemId);
            
            const index = MOCK_DATA.inventory.findIndex(i => i.id === itemId);
            if (index > -1) {
                MOCK_DATA.inventory.splice(index, 1);
                this.loadData();
                this.showToast('Item deleted successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to delete item:', error);
            this.showToast('Failed to delete item', 'error');
        }
    },
    
    /**
     * Show create inventory modal
     */
    showCreateModal() {
        let modal = document.getElementById('inventoryModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'inventoryModal';
            modal.className = 'modal-overlay';
            document.body.appendChild(modal);
        }
        
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3><i class="fas fa-box" style="color: var(--success);"></i> Add Inventory Item</h3>
                    <button class="modal-close" onclick="document.getElementById('inventoryModal').classList.remove('active')">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <form id="createInventoryForm" onsubmit="Inventory.createItem(event)">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Item Name *</label>
                            <input type="text" id="invName" required placeholder="e.g., Raw Material X" />
                        </div>
                        <div class="form-group">
                            <label>SKU *</label>
                            <input type="text" id="invSku" required placeholder="e.g., RM-001" />
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Quantity *</label>
                            <input type="number" id="invQuantity" required min="0" placeholder="0" />
                        </div>
                        <div class="form-group">
                            <label>Min. Stock *</label>
                            <input type="number" id="invMinStock" required min="0" placeholder="10" />
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Unit *</label>
                        <select id="invUnit" required>
                            <option value="pcs">Pieces (pcs)</option>
                            <option value="kg">Kilograms (kg)</option>
                            <option value="g">Grams (g)</option>
                            <option value="L">Liters (L)</option>
                            <option value="m">Meters (m)</option>
                        </select>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline" onclick="document.getElementById('inventoryModal').classList.remove('active')">
                            Cancel
                        </button>
                        <button type="submit" class="btn btn-success">
                            <i class="fas fa-plus"></i> Add Item
                        </button>
                    </div>
                </form>
            </div>
        `;
        
        modal.classList.add('active');
    },
    
    /**
     * Create new inventory item
     */
    async createItem(event) {
        event.preventDefault();
        
        const name = document.getElementById('invName').value.trim();
        const sku = document.getElementById('invSku').value.trim();
        const quantity = parseInt(document.getElementById('invQuantity').value);
        const minStock = parseInt(document.getElementById('invMinStock').value);
        const unit = document.getElementById('invUnit').value;
        
        if (!name || !sku || isNaN(quantity) || isNaN(minStock)) {
            this.showToast('Please fill all required fields', 'error');
            return;
        }
        
        try {
            // In production: await API.inventory.create({ name, sku, quantity, minStock, unit });
            
            const newItem = {
                id: MOCK_DATA.inventory.length + 1,
                name,
                sku,
                quantity,
                minStock,
                unit,
            };
            MOCK_DATA.inventory.push(newItem);
            
            document.getElementById('inventoryModal').classList.remove('active');
            this.loadData();
            this.showToast(`${name} added to inventory!`, 'success');
            
        } catch (error) {
            console.error('Failed to create item:', error);
            this.showToast('Failed to add item', 'error');
        }
    },
    
    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
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
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
};