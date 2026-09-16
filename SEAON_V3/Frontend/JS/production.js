/**
 * Production Module - Manages manufacturing jobs
 * Track production runs, operators, and output
 */

const Production = {
    /**
     * Current production data
     */
    jobs: [],
    
    /**
     * Render production page
     */
    render(container) {
        if (!container) return;
        
        container.innerHTML = `
            <div class="page-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px;">
                <div>
                    <h1 style="font-size: 28px; font-weight: 700;">Production</h1>
                    <p style="color: var(--gray-500);">Manage manufacturing jobs and production runs</p>
                </div>
                <button class="btn btn-success" onclick="Production.showCreateModal()">
                    <i class="fas fa-play"></i> Start Production
                </button>
            </div>
            
            <!-- Production Table -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Production Jobs</h3>
                    <button class="btn btn-sm btn-outline" onclick="Production.loadData()">
                        <i class="fas fa-refresh"></i> Refresh
                    </button>
                </div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Job ID</th>
                                <th>Product</th>
                                <th>Quantity</th>
                                <th>Status</th>
                                <th>Start Date</th>
                                <th>Operator</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="productionTableBody">
                            <tr><td colspan="7" style="text-align:center; padding: 40px; color: var(--gray-400);">
                                <i class="fas fa-spinner fa-spin"></i> Loading production jobs...
                            </td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        this.loadData();
    },
    
    /**
     * Load production data
     */
    async loadData() {
        try {
            // In production: const data = await API.production.getAll();
            const jobs = [...MOCK_DATA.production];
            this.jobs = jobs;
            this.renderTable(jobs);
            
        } catch (error) {
            console.error('Failed to load production:', error);
            document.getElementById('productionTableBody').innerHTML = `
                <tr><td colspan="7" style="text-align:center; padding: 40px; color: var(--danger);">
                    <i class="fas fa-exclamation-circle"></i> Failed to load production data
                </td></tr>
            `;
        }
    },
    
    /**
     * Render production table
     */
    renderTable(jobs) {
        const tbody = document.getElementById('productionTableBody');
        if (!tbody) return;
        
        if (jobs.length === 0) {
            tbody.innerHTML = `
                <tr><td colspan="7" style="text-align:center; padding: 60px 20px; color: var(--gray-400);">
                    <i class="fas fa-industry" style="font-size: 36px; display: block; margin-bottom: 12px;"></i>
                    No production jobs scheduled
                </td></tr>
            `;
            return;
        }
        
        tbody.innerHTML = jobs.map(job => `
            <tr>
                <td><strong>#${job.id}</strong></td>
                <td>${job.product}</td>
                <td>${job.quantity}</td>
                <td>
                    <span class="status-badge ${job.status}">${this.capitalize(job.status)}</span>
                </td>
                <td>${this.formatDate(job.startDate)}</td>
                <td>${job.operator || 'Unassigned'}</td>
                <td>
                    <div style="display: flex; gap: 6px;">
                        ${job.status !== 'completed' ? `
                            <button class="btn btn-sm btn-success" onclick="Production.completeJob(${job.id})" title="Complete Job">
                                <i class="fas fa-check"></i>
                            </button>
                            <button class="btn btn-sm btn-outline" onclick="Production.assignOperator(${job.id})" title="Assign Operator">
                                <i class="fas fa-user-plus"></i>
                            </button>
                        ` : ''}
                        <button class="btn btn-sm btn-danger" onclick="Production.deleteJob(${job.id})" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    },
    
    /**
     * Complete a production job
     */
    async completeJob(jobId) {
        const output = prompt('Enter quantity produced:');
        if (output === null) return;
        
        const quantity = parseInt(output);
        if (isNaN(quantity) || quantity <= 0) {
            this.showToast('Please enter a valid quantity', 'error');
            return;
        }
        
        try {
            // In production: await API.production.completeJob(jobId, { quantity });
            
            const job = MOCK_DATA.production.find(j => j.id === jobId);
            if (job) {
                job.status = 'completed';
                this.loadData();
                this.showToast(`Job #${jobId} completed! Produced ${quantity} units.`, 'success');
            }
        } catch (error) {
            console.error('Failed to complete job:', error);
            this.showToast('Failed to complete production job', 'error');
        }
    },
    
    /**
     * Assign operator to job
     */
    async assignOperator(jobId) {
        const operator = prompt('Enter operator name:');
        if (operator === null || operator.trim() === '') return;
        
        try {
            const job = MOCK_DATA.production.find(j => j.id === jobId);
            if (job) {
                job.operator = operator.trim();
                this.loadData();
                this.showToast(`Operator "${operator}" assigned to job #${jobId}`, 'success');
            }
        } catch (error) {
            console.error('Failed to assign operator:', error);
            this.showToast('Failed to assign operator', 'error');
        }
    },
    
    /**
     * Delete production job
     */
    async deleteJob(jobId) {
        if (!confirm(`Delete production job #${jobId}?`)) return;
        
        try {
            const index = MOCK_DATA.production.findIndex(j => j.id === jobId);
            if (index > -1) {
                MOCK_DATA.production.splice(index, 1);
                this.loadData();
                this.showToast(`Job #${jobId} deleted`, 'success');
            }
        } catch (error) {
            console.error('Failed to delete job:', error);
            this.showToast('Failed to delete job', 'error');
        }
    },
    
    /**
     * Show create production modal
     */
    showCreateModal() {
        let modal = document.getElementById('productionModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'productionModal';
            modal.className = 'modal-overlay';
            document.body.appendChild(modal);
        }
        
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3><i class="fas fa-play-circle" style="color: var(--success);"></i> Start New Production Job</h3>
                    <button class="modal-close" onclick="document.getElementById('productionModal').classList.remove('active')">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <form id="createProductionForm" onsubmit="Production.createJob(event)">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Product *</label>
                            <select id="prodProduct" required>
                                <option value="">Select Product</option>
                                <option value="Widget A">Widget A</option>
                                <option value="Widget B">Widget B</option>
                                <option value="Widget C">Widget C</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Quantity *</label>
                            <input type="number" id="prodQuantity" required min="1" placeholder="e.g., 100" />
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Operator</label>
                        <input type="text" id="prodOperator" placeholder="e.g., Jane Smith" />
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline" onclick="document.getElementById('productionModal').classList.remove('active')">
                            Cancel
                        </button>
                        <button type="submit" class="btn btn-success">
                            <i class="fas fa-play"></i> Start Production
                        </button>
                    </div>
                </form>
            </div>
        `;
        
        modal.classList.add('active');
    },
    
    /**
     * Create new production job
     */
    async createJob(event) {
        event.preventDefault();
        
        const product = document.getElementById('prodProduct').value;
        const quantity = parseInt(document.getElementById('prodQuantity').value);
        const operator = document.getElementById('prodOperator').value.trim() || 'Unassigned';
        
        if (!product || !quantity) {
            this.showToast('Please fill all required fields', 'error');
            return;
        }
        
        try {
            // In production: await API.production.startJob({ product, quantity, operator });
            
            const newJob = {
                id: MOCK_DATA.production.length + 1,
                product,
                quantity,
                status: 'pending',
                startDate: new Date().toISOString().split('T')[0],
                operator,
            };
            MOCK_DATA.production.unshift(newJob);
            
            document.getElementById('productionModal').classList.remove('active');
            this.loadData();
            this.showToast(`Production job #${newJob.id} started for ${product}!`, 'success');
            
        } catch (error) {
            console.error('Failed to start production:', error);
            this.showToast('Failed to start production', 'error');
        }
    },
    
    /**
     * Format date
     */
    formatDate(dateStr) {
        if (!dateStr) return '-';
        const d = new Date(dateStr);
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    },
    
    /**
     * Capitalize
     */
    capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    },
    
    /**
     * Show toast
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