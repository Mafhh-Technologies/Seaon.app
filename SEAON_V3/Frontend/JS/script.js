// TOAST NOTIFICATIONS SYSTEM
const Toast = {
    /**
     * Show a toast notification
     * @param {string} message - Toast message
     * @param {string} type - 'success', 'error', 'warning', 'info'
     * @param {number} duration - Duration in ms (default: 4000)
     */
    show(message, type = 'info', duration = 4000) {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };

        toast.innerHTML = `
            <i class="fas ${icons[type] || icons.info}"></i>
            <span>${escapeHTML(message)}</span>
        `;

        container.appendChild(toast);

        // Auto-remove after duration
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.remove();
                }
            }, 400);
        }, duration);
    },

    success(message, duration) {
        this.show(message, 'success', duration);
    },

    error(message, duration) {
        this.show(message, 'error', duration);
    },

    warning(message, duration) {
        this.show(message, 'warning', duration);
    },

    info(message, duration) {
        this.show(message, 'info', duration);
    }
};

// CONFIRMATION DIALOG

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// DATE FORMATTING

function formatDate(date) {
    if (!date) return '-';
    const d = new Date(date);
    return d.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatDateTime(date) {
    if (!date) return '-';
    const d = new Date(date);
    return d.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// SEARCH HIGHLIGHTING

function highlightText(text, query) {
    if (!query || !text) return escapeHTML(text);
    const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
    return escapeHTML(text).replace(regex, '<mark>$1</mark>');
}

function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// EXPORT FUNCTIONS

function exportToCSV(data, filename = 'export.csv') {
    if (!data || data.length === 0) {
        Toast.warning('No data to export');
        return;
    }

    const headers = Object.keys(data[0]);
    const csvRows = [];

    // Add headers
    csvRows.push(headers.join(','));

    // Add rows
    for (const row of data) {
        const values = headers.map(header => {
            const val = row[header] || '';
            return `"${String(val).replace(/"/g, '""')}"`;
        });
        csvRows.push(values.join(','));
    }

    const csvContent = csvRows.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);

    Toast.success(`Exported ${data.length} items to CSV`);
}


// KEYBOARD SHORTCUTS
document.addEventListener('keydown', function(e) {
    // Cmd+K or Ctrl+K for search
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('.search-box input');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }

    // Escape to close modals
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.show, .product-modal.show, .adjust-modal.show')
            .forEach(modal => modal.classList.remove('show'));
        closeMobileDrawer();
    }
});


// NOTIFICATION SYSTEM ENHANCEMENT
function createNotification(title, message, type = 'info', link = null) {
    const notifications = readStorage('notifications', []);
    
    const notification = {
        id: generateId(),
        title,
        message,
        type,
        link,
        read: false,
        timestamp: new Date().toISOString()
    };

    notifications.unshift(notification);
    localStorage.setItem('notifications', JSON.stringify(notifications));

    updateNotificationBadge();
    return notification;
}

function updateNotificationBadge() {
    const notifications = readStorage('notifications', []);
    const unread = notifications.filter(n => !n.read).length;
    const badge = document.getElementById('notificationCount');
    const bellDot = document.getElementById('bellDot');
    const unreadBadge = document.getElementById('unreadBadge');

    if (badge) {
        badge.textContent = unread;
        badge.style.display = unread > 0 ? 'flex' : 'none';
    }

    if (bellDot) {
        bellDot.classList.toggle('active', unread > 0);
    }

    if (unreadBadge) {
        unreadBadge.innerHTML = `<i class="fas fa-circle"></i> ${unread} Unread`;
    }
}

// REFRESH BUTTON WITH SPINNER

document.querySelectorAll('.refresh-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const icon = this.querySelector('i');
        icon.classList.add('fa-spin');
        setTimeout(() => {
            refreshApplication();
            icon.classList.remove('fa-spin');
            Toast.success('Data refreshed successfully');
        }, 500);
    });
});

// EXPORT BUTTONS

document.getElementById('exportDashboard')?.addEventListener('click', function() {
    const data = productionOrders.map(order => ({
        'Order ID': order.id,
        'Customer': order.customerName,
        'Product': order.productName,
        'Quantity': order.quantity,
        'Status': order.status,
        'Date': order.date
    }));
    exportToCSV(data, 'dashboard_orders.csv');
});

document.getElementById('exportInventory')?.addEventListener('click', function() {
    const data = inventory.map(item => ({
        'Item Name': item.itemName,
        'Type': item.type,
        'Quantity': item.availableQuantity,
        'Unit': item.unit,
        'Min Stock': item.minimumStock,
        'Location': item.location,
        'Status': isLowStock(item) ? 'Low Stock' : 'OK'
    }));
    exportToCSV(data, 'inventory_export.csv');
});

document.getElementById('exportProduction')?.addEventListener('click', function() {
    const data = productionOrders.map(order => ({
        'Order ID': order.id,
        'Customer': order.customerName,
        'Product': order.productName,
        'Quantity': order.quantity,
        'Status': order.status,
        'Date': order.date
    }));
    exportToCSV(data, 'production_export.csv');
});

// AUTO-REFRESH ON STORAGE CHANGE
window.addEventListener('storage', function(e) {
    if (e.key === 'inventory' || e.key === 'productionOrders' || e.key === 'bomData') {
        inventory = readStorage('inventory', []);
        productionOrders = readStorage('productionOrders', []);
        bomData = readStorage('bomData', {});
        refreshApplication();
    }
});

// INITIALIZE NOTIFICATION BADGE
updateNotificationBadge();

// GLOBAL SEARCH ENHANCEMENT
document.getElementById('globalSearch')?.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        const query = this.value.trim().toLowerCase();
        if (!query) return;

        // Search in inventory
        const inventoryResults = inventory.filter(item => 
            item.itemName.toLowerCase().includes(query) ||
            item.type.toLowerCase().includes(query)
        );

        // Search in orders
        const orderResults = productionOrders.filter(order =>
            order.customerName.toLowerCase().includes(query) ||
            order.productName.toLowerCase().includes(query) ||
            order.id.toLowerCase().includes(query)
        );

        if (inventoryResults.length > 0 || orderResults.length > 0) {
            Toast.info(`Found ${inventoryResults.length} items and ${orderResults.length} orders`);
            showPage('dashboardPage');
        } else {
            Toast.warning('No results found');
        }
    }
});S