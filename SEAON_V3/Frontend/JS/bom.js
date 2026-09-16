/**
 * BOM Module - Bill of Materials
 * Manage product components and material requirements
 */

const BOM = {
    /**
     * Current BOM data
     */
    items: [],
    
    /**
     * Render BOM page
     */
    render(container) {
        if (!container) return;
        
        container.innerHTML = `
            <div class="page-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px;">
                <div>
                    <h1 style="font-size: 28px; font-weight: 700;">Bill of Materials (BOM)</h1>
                    <p style="color: var(--gray-500);">View component requirements for each product</p>
                </div>
                <button class="btn btn-primary" onclick="BOM.showCreateModal()">
                    <i class="fas fa-plus"></i> Add BOM Item
                </button>
            </div>
            
            <!-- Product Filter -->
            <div style="display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; align-items: center;">
                <label style="font-weight: 500;">Filter by Product:</label>
                <select id="bomProductFilter" style="padding: 8px 14px; border-radius: 6px; border: 1px solid var(--gray-200); background: white; min-width: 150px;">
                    <option value="all">All Products</option>
                    <option value="Widget A">Widget A</option>
                    <option value="Widget B">Widget B</option>
                    <option value="Widget C">Widget C</option>
                </select>
                <button class="btn btn-sm btn-outline" onclick="BOM.loadData()">
                    <i class="fas fa-refresh"></i> Refresh
                </button>
            </div>
            
            <!-- BOM Table -->
            <div class="card">
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th>Component</th>
                                <th>Quantity</th>
                                <th>Unit</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="bomTableBody">
                            <tr><td colspan="5" style="text-align:center; padding: 40px; color: var(--gray-400);">
                                <i class="fas fa-spinner fa-spin"></i> Loading BOM data...
                            </td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        // Setup event listeners
        document.getElementById('bomProductFilter')?.addEventListener('change', () => this.loadData());
        
        this.loadData();
    },
    
    /**
     * Load BOM data
     */
    async loadData() {
        try {
            // In production: const data = await API.bom.getAll();
            let items = [...MOCK_DATA.bom];
            
            // Apply filter
            const filter = document.getElementById('bomProductFilter')?.value;
            if (filter && filter !== 'all') {
                items = items.filter(item => item.product === filter);
            }
            
            this.items = items;
            this.renderTable(items);
            
        } catch (error) {
            console.error('Failed to load BOM:', error);
            document.getElementById('bomTableBody').innerHTML = `
                <tr><td colspan="5" style="text-align:center; padding: 40px; color: var(--danger);">
                    <i class="fas fa-exclamation-circle"></i> Failed to load BOM data
                </td></tr>
            `;
        }
    },
    
    /**
     * Render BOM table
     */
    renderTable(items) {
        const tbody = document.getElementById('bomTableBody');
        if (!tbody) return;
        
        if (items.length === 0) {
            tbody.innerHTML = `
                <tr><td colspan="5" style="text-align:center; padding: 60px 20px; color: var(--gray-400);">
                    <i class="fas fa-list" style="font-size: 36px; display: block; margin-bottom: 12px;"></i>
                    No BOM items found for this product
                </td></tr>
            `;
            return;
        }
        
        tbody.innerHTML = items.map(item => `
            <tr>
                <td><strong>${item.product}</strong></td>
                <td>${item.component}</td>
                <td>${item.quantity}</td>
                <td>${item.unit}</td>
                <td>
                    <div style="display: flex; gap: 6px;">
                        <button class="btn btn-sm btn-outline" onclick="BOM.editItem(${item.id})" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="BOM.deleteItem(${item.id})" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    },
    
    /**
     * Delete BOM item
     */
    async deleteItem(itemId) {
        if (!confirm('Delete this BOM entry?')) return;
        
        try {
            const index = MOCK_DATA.bom.findIndex(i => i.id === itemId);
            if (index > -1) {
                MOCK_DATA.bom.splice(index, 1);
                this.loadData();
                this.showToast('BOM entry deleted', 'success');
            }
        } catch (error) {
            console.error('Failed to delete BOM:', error);
            this.showToast('Failed to delete BOM entry', 'error');
        }
    },
    
    /**
     * Edit BOM item (simple inline edit)
     */
    editItem(itemId) {
        const item = MOCK_DATA.bom.find(i => i.id === itemId);
        if (!item) return;
        
        const newQuantity = prompt(`Enter new quantity for ${item.component}:`, item.quantity);
        if (newQuantity === null) return;
        
        const quantity = parseFloat(newQuantity);
        if (isNaN(quantity) || quantity <= 0) {
            this.showToast('Please enter a valid quantity', 'error');
            return;
        }
        
        item.quantity = quantity;
        this.loadData();
        this.showToast(`BOM entry updated: ${item.component} → ${quantity} ${item.unit}`, 'success');
    },
    
    /**
     * Show create BOM modal
     */
    showCreateModal() {
        let modal = document.getElementById('bomModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'bomModal';
            modal.className = 'modal-overlay';
            document.body.appendChild(modal);
        }
        
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3><i class="fas fa-list" style="color: var(--primary);"></i> Add BOM Entry</h3>
                    <button class="modal-close" onclick="document.getElementById('bomModal').classList.remove('active')">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <form id="createBomForm" onsubmit="BOM.createItem(event)">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Product *</label>
                            <select id="bomProduct" required>
                                <option value="">Select Product</option>
                                <option value="Widget A">Widget A</option>
                                <option value="Widget B">Widget B</option>
                                <option value="Widget C">Widget C</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Component *</label>
                            <input type="text" id="bomComponent" required placeholder="e.g., Raw Material X" />
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Quantity *</label>
                            <input type="number" id="bomQuantity" required min="0.1" step="0.1" placeholder="e.g., 2.5" />
                        </div>
                        <div class="form-group">
                            <label>Unit *</label>
                            <select id="bomUnit" required>
                                <option value="kg">Kilograms (kg)</option>
                                <option value="g">Grams (g)</option>
                                <option value="pcs">Pieces (pcs)</option>
                                <option value="L">Liters (L)</option>
                                <option value="m">Meters (m)</option>
                            </select>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline" onclick="document.getElementById('bomModal').classList.remove('active')">
                            Cancel
                        </button>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-plus"></i> Add BOM Entry
                        </button>
                    </div>
                </form>
            </div>
        `;
        
        modal.classList.add('active');
    },
    
    /**
     * Create new BOM entry
     */
    async createItem(event) {
        event.preventDefault();
        
        const product = document.getElementById('bomProduct').value;
        const component = document.getElementById('bomComponent').value.trim();
        const quantity = parseFloat(document.getElementById('bomQuantity').value);
        const unit = document.getElementById('bomUnit').value;
        
        if (!product || !component || !quantity) {
            this.showToast('Please fill all required fields', 'error');
            return;
        }
        
        try {
            // In production: await API.bom.create({ product, component, quantity, unit });
            
            const newItem = {
                id: MOCK_DATA.bom.length + 1,
                product,
                component,
                quantity,
                unit,
            };
            MOCK_DATA.bom.push(newItem);
            
            document.getElementById('bomModal').classList.remove('active');
            this.loadData();
            this.showToast(`BOM entry added: ${component} → ${product}`, 'success');
            
        } catch (error) {
            console.error('Failed to create BOM:', error);
            this.showToast('Failed to add BOM entry', 'error');
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