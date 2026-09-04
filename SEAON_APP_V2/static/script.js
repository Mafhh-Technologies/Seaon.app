/* =========================================================
   SEON ERP - Inventory Frontend
   IMPORTANT: This file talks to Flask using /api/... routes.
   Open the website through http://127.0.0.1:5000, not by
   double-clicking index.html.
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
    const $ = (id) => document.getElementById(id);

    let inventory = [];
    let editingProductId = null;
    let adjustingProductId = null;

    // ---------------------------------------------------------
    // API HELPER
    // ---------------------------------------------------------
    const API_BASE = "http://127.0.0.1:5000";

    async function api(url, options = {}) {
        if (window.location.protocol === "file:") {
            throw new Error("Open SEON through http://127.0.0.1:5000. Do not open index.html directly.");
        }

        const finalUrl = url.startsWith("http") ? url : API_BASE + url;

        const response = await fetch(finalUrl, {
            method: "GET",
            ...options,
            headers: {
                Accept: "application/json",
                ...(options.body ? { "Content-Type": "application/json" } : {}),
                ...(options.headers || {})
            }
        });

        const contentType = response.headers.get("content-type") || "";
        const data = contentType.includes("application/json")
            ? await response.json()
            : { error: await response.text() };

        if (!response.ok) {
            throw new Error(data.error || `Request failed (${response.status})`);
        }

        return data;
    }

    function showMessage(message, type = "success") {
        const result = $("result");
        if (!result) {
            alert(message);
            return;
        }
        result.innerHTML = `<p class="${type}">${escapeHtml(message)}</p>`;
        clearTimeout(showMessage.timer);
        showMessage.timer = setTimeout(() => {
            result.innerHTML = "";
        }, 3500);
    }

    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function formatNumber(value) {
        return Number(value || 0).toLocaleString(undefined, {
            maximumFractionDigits: 2
        });
    }

    // ---------------------------------------------------------
    // PAGE NAVIGATION
    // ---------------------------------------------------------
    function showPage(pageId) {
        document.querySelectorAll(".page").forEach((page) => {
            page.classList.remove("active-page");
        });

        const page = $(pageId);
        if (page) page.classList.add("active-page");

        document.querySelectorAll(".menu").forEach((menu) => {
            menu.classList.toggle("active", menu.dataset.page === pageId);
        });

        if (pageId === "inventoryPage" || pageId === "dashboardPage") {
            loadInventory();
        }
    }

    document.querySelectorAll(".menu").forEach((menu) => {
        menu.addEventListener("click", (event) => {
            event.preventDefault();
            showPage(menu.dataset.page);
        });
    });

    document.querySelector(".manage-btn")?.addEventListener("click", (event) => {
        event.preventDefault();
        showPage("inventoryPage");
    });

    document.querySelector(".go-orders")?.addEventListener("click", (event) => {
        event.preventDefault();
        showPage("createOrderPage");
    });

    // ---------------------------------------------------------
    // INVENTORY LOAD
    // ---------------------------------------------------------
    async function loadInventory() {
        try {
            inventory = await api("/api/products");
            renderInventory();
            updateInventoryStats();
            updateDashboard();
            populateProductDropdowns();
            updateNotifications();
        } catch (error) {
            console.error("Inventory load error:", error);
            showMessage(error.message, "error");
        }
    }

    // ---------------------------------------------------------
    // INVENTORY RENDER
    // ---------------------------------------------------------
    function renderInventory() {
        const body = $("inventoryBody");
        if (!body) return;

        const search = ($("inventorySearch")?.value || "").trim().toLowerCase();
        const selectedType = $("inventoryType")?.value || "all";
        const selectedStatus = $("inventoryStatus")?.value || "all";

        const filtered = inventory.filter((product) => {
            const text = [
                product.itemName,
                product.category,
                product.type,
                product.color,
                product.sizeDescription,
                product.location
            ].join(" ").toLowerCase();

            const typeMatch = selectedType === "all" || product.type === selectedType;
            const status = product.status;
            const statusMatch = selectedStatus === "all" || status === selectedStatus;

            return text.includes(search) && typeMatch && statusMatch;
        });

        body.innerHTML = "";

        if (!filtered.length) {
            body.innerHTML = `
                <tr>
                    <td colspan="11" style="text-align:center;padding:30px;color:#64748b;">
                        No inventory items found.
                    </td>
                </tr>`;
            return;
        }

        filtered.forEach((product) => {
            const lowStock = product.status === "Low Stock";
            const rawMaterial = product.type === "Raw Material";

            const row = document.createElement("tr");
            row.innerHTML = `
                <td class="inventory-item-name">${escapeHtml(product.itemName)}</td>
                <td><span class="inventory-type">${escapeHtml(product.type)}</span></td>
                <td class="raw-material-column">${rawMaterial ? escapeHtml(product.thickness || "-") : "-"}</td>
                <td class="raw-material-column">${rawMaterial ? escapeHtml(product.sizeDescription || "-") : "-"}</td>
                <td class="raw-material-column">${rawMaterial ? escapeHtml(product.color || "-") : "-"}</td>
                <td class="${lowStock ? "low-quantity" : ""}">${formatNumber(product.availableQuantity)}</td>
                <td>${escapeHtml(product.unit)}</td>
                <td>${formatNumber(product.minimumStock)}</td>
                <td>${escapeHtml(product.location)}</td>
                <td>
                    <span class="inventory-status ${lowStock ? "status-low" : "status-ok"}">
                        ${escapeHtml(product.status)}
                    </span>
                </td>
                <td>
                    <div class="inventory-actions">
                        <button type="button" class="edit-inventory" data-id="${product.id}">Edit</button>
                        <button type="button" class="adjust-inventory" data-id="${product.id}">✎ Adjust</button>
                        <button type="button" class="delete-inventory" data-id="${product.id}">🗑 Delete</button>
                    </div>
                </td>
            `;
            body.appendChild(row);
        });

        body.querySelectorAll(".edit-inventory").forEach((button) => {
            button.addEventListener("click", () => openEditModal(Number(button.dataset.id)));
        });
        body.querySelectorAll(".adjust-inventory").forEach((button) => {
            button.addEventListener("click", () => openAdjustModal(Number(button.dataset.id)));
        });
        body.querySelectorAll(".delete-inventory").forEach((button) => {
            button.addEventListener("click", () => deleteProduct(Number(button.dataset.id)));
        });
    }

    function updateInventoryStats() {
        const low = inventory.filter((p) => p.status === "Low Stock").length;
        const ok = inventory.length - low;
        if ($("totalItems")) $("totalItems").textContent = inventory.length;
        if ($("lowStockCount")) $("lowStockCount").textContent = low;
        if ($("okStockCount")) $("okStockCount").textContent = ok;
    }

    // ---------------------------------------------------------
    // DASHBOARD
    // ---------------------------------------------------------
    function updateDashboard() {
        const low = inventory.filter((p) => p.status === "Low Stock");

        if ($("lowStockAlerts")) $("lowStockAlerts").textContent = low.length;
        if ($("stockMessage")) {
            $("stockMessage").textContent = low.length
                ? `${low.length} item(s) need attention`
                : "All stocks are healthy";
        }

        if ($("lowStockList")) {
            $("lowStockList").innerHTML = low.length
                ? low.slice(0, 8).map((product) => `
                    <div class="stock-item critical">
                        <div class="stock-alert-icon">!</div>
                        <div class="stock-content">
                            <strong>${escapeHtml(product.itemName)}</strong>
                            <small>${escapeHtml(product.type)}</small>
                            <p>
                                Current: <b>${formatNumber(product.availableQuantity)} ${escapeHtml(product.unit)}</b>
                                | Min: ${formatNumber(product.minimumStock)} ${escapeHtml(product.unit)}
                            </p>
                        </div>
                    </div>
                `).join("")
                : `<p class="no-low-stock">No low stock items</p>`;
        }

        // Orders/production are not connected yet, so keep these at zero honestly.
        if ($("totalOrders")) $("totalOrders").textContent = "0";
        if ($("pendingProduction")) $("pendingProduction").textContent = "0";
        if ($("completedOrders")) $("completedOrders").textContent = "0";
        if ($("ordersChange")) $("ordersChange").textContent = "No orders yet";
        if ($("pendingChange")) $("pendingChange").textContent = "No production orders";
        if ($("completedChange")) $("completedChange").textContent = "No completed orders";
    }

    // ---------------------------------------------------------
    // ADD PRODUCT
    // ---------------------------------------------------------
    function openAddModal() {
        $("productForm")?.reset();
        toggleRawFields();
        $("productModal")?.classList.add("show");
    }

    function closeAddModal() {
        $("productModal")?.classList.remove("show");
    }

    $("addProductBtn")?.addEventListener("click", openAddModal);
    $("closeProductModal")?.addEventListener("click", closeAddModal);
    $("cancelProduct")?.addEventListener("click", closeAddModal);

    $("productType")?.addEventListener("change", toggleRawFields);

    function toggleRawFields() {
        const isRaw = $("productType")?.value === "Raw Material";
        document.querySelectorAll(".raw-material-field").forEach((field) => {
            field.style.display = isRaw ? "flex" : "none";
        });
    }

    $("productForm")?.addEventListener("submit", async (event) => {
        event.preventDefault();

        const product = collectProductForm("product");
        const button = event.submitter;
        if (button) button.disabled = true;

        try {
            const result = await api("/api/products", {
                method: "POST",
                body: JSON.stringify(product)
            });

            closeAddModal();
            event.target.reset();
            await loadInventory();
            showMessage(`Product added successfully. ID: ${result.id}`, "success");
        } catch (error) {
            console.error("Add product error:", error);
            showMessage(error.message, "error");
        } finally {
            if (button) button.disabled = false;
        }
    });

    function collectProductForm(prefix) {
        const get = (id) => $(prefix === "product" ? `product${id}` : `editProduct${id}`);
        const type = get("Type").value;
        return {
            itemName: get("Name").value.trim(),
            category: type === "Raw Material" ? "Raw Material" : type,
            type,
            thickness: get("Thickness")?.value || "",
            sizeDescription: get("Size")?.value.trim() || "",
            color: get("Color")?.value.trim() || "",
            availableQuantity: Number(get("Quantity").value),
            unit: get("Unit").value,
            minimumStock: Number(get("Minimum").value),
            location: get("Location").value.trim()
        };
    }

    // ---------------------------------------------------------
    // EDIT PRODUCT
    // ---------------------------------------------------------
    function ensureEditModal() {
        if ($("editProductModal")) return;

        const modal = document.createElement("div");
        modal.className = "product-modal";
        modal.id = "editProductModal";
        modal.innerHTML = `
            <div class="modal-box">
                <div class="modal-header">
                    <h3>Edit Product</h3>
                    <button type="button" id="closeEditProductModal">×</button>
                </div>
                <form id="editProductForm">
                    <div class="modal-form">
                        <div class="form-group"><label>Item Name</label><input id="editProductName" type="text" required></div>
                        <div class="form-group"><label>Type</label>
                            <select id="editProductType" required>
                                <option value="">Select Type</option>
                                <option value="Raw Material">Raw Material</option>
                                <option value="Semi Finished Product">Semi Finished Product</option>
                                <option value="Finished Product">Finished Product</option>
                            </select>
                        </div>
                        <div class="form-group"><label>Thickness (mm)</label><input id="editProductThickness" type="number" min="0" step="0.01"></div>
                        <div class="form-group"><label>Size</label><input id="editProductSize" type="text"></div>
                        <div class="form-group"><label>Color</label><input id="editProductColor" type="text"></div>
                        <div class="form-group"><label>Available Quantity</label><input id="editProductQuantity" type="number" min="0" required></div>
                        <div class="form-group"><label>Unit</label>
                            <select id="editProductUnit" required>
                                <option value="">Select Unit</option>
                                <option value="kg">kg</option><option value="m">m</option><option value="pcs">pcs</option>
                                <option value="rolls">rolls</option><option value="Boxes">Boxes</option><option value="Nos">Nos</option>
                            </select>
                        </div>
                        <div class="form-group"><label>Minimum Stock</label><input id="editProductMinimum" type="number" min="0" required></div>
                        <div class="form-group"><label>Location</label><input id="editProductLocation" type="text" required></div>
                    </div>
                    <div class="modal-buttons">
                        <button type="button" id="cancelEditProduct" class="cancel-product-btn">Cancel</button>
                        <button type="submit" class="save-product-btn">Save Changes</button>
                    </div>
                </form>
            </div>`;
        document.body.appendChild(modal);

        $("closeEditProductModal").addEventListener("click", closeEditModal);
        $("cancelEditProduct").addEventListener("click", closeEditModal);
        $("editProductForm").addEventListener("submit", saveEditProduct);
        $("editProductType").addEventListener("change", () => {
            const isRaw = $("editProductType").value === "Raw Material";
            ["editProductThickness", "editProductSize", "editProductColor"].forEach((id) => {
                const group = $(id)?.closest(".form-group");
                if (group) group.style.display = isRaw ? "flex" : "none";
            });
        });
    }

    function openEditModal(productId) {
        ensureEditModal();
        const product = inventory.find((item) => item.id === productId);
        if (!product) return;

        editingProductId = productId;
        $("editProductName").value = product.itemName;
        $("editProductType").value = product.type;
        $("editProductThickness").value = product.thickness || "";
        $("editProductSize").value = product.sizeDescription || "";
        $("editProductColor").value = product.color || "";
        $("editProductQuantity").value = product.availableQuantity;
        $("editProductUnit").value = product.unit;
        $("editProductMinimum").value = product.minimumStock;
        $("editProductLocation").value = product.location;
        $("editProductType").dispatchEvent(new Event("change"));
        $("editProductModal").classList.add("show");
    }

    function closeEditModal() {
        $("editProductModal")?.classList.remove("show");
        editingProductId = null;
    }

    async function saveEditProduct(event) {
        event.preventDefault();
        if (!editingProductId) return;

        const product = collectProductForm("editProduct");
        const button = event.submitter;
        if (button) button.disabled = true;

        try {
            await api(`/api/products/${editingProductId}`, {
                method: "PUT",
                body: JSON.stringify(product)
            });
            closeEditModal();
            await loadInventory();
            showMessage("Product updated successfully.", "success");
        } catch (error) {
            console.error("Edit product error:", error);
            showMessage(error.message, "error");
        } finally {
            if (button) button.disabled = false;
        }
    }

    // ---------------------------------------------------------
    // ADJUST STOCK
    // ---------------------------------------------------------
    function openAdjustModal(productId) {
        const product = inventory.find((item) => item.id === productId);
        if (!product) return;

        adjustingProductId = productId;
        $("adjustItemName").textContent = product.itemName;
        $("adjustItemType").textContent = product.type;
        $("adjustCurrentQuantity").textContent = `${formatNumber(product.availableQuantity)} ${product.unit}`;
        $("adjustNewQuantity").value = product.availableQuantity;
        $("adjustUnit").textContent = product.unit;
        $("adjustModal").classList.add("show");
    }

    function closeAdjustModal() {
        $("adjustModal")?.classList.remove("show");
        adjustingProductId = null;
    }

    $("closeAdjustModal")?.addEventListener("click", closeAdjustModal);
    $("cancelAdjust")?.addEventListener("click", closeAdjustModal);

    $("saveAdjust")?.addEventListener("click", async () => {
        if (!adjustingProductId) return;

        const quantity = Number($("adjustNewQuantity").value);
        if (!Number.isFinite(quantity) || quantity < 0) {
            showMessage("Please enter a valid quantity.", "error");
            return;
        }

        const button = $("saveAdjust");
        button.disabled = true;

        try {
            await api(`/api/products/${adjustingProductId}/stock`, {
                method: "PATCH",
                body: JSON.stringify({
                    availableQuantity: quantity,
                    note: "Manual stock adjustment from Inventory"
                })
            });
            closeAdjustModal();
            await loadInventory();
            showMessage("Stock updated successfully.", "success");
        } catch (error) {
            console.error("Adjust stock error:", error);
            showMessage(error.message, "error");
        } finally {
            button.disabled = false;
        }
    });

    // ---------------------------------------------------------
    // DELETE PRODUCT
    // ---------------------------------------------------------
    async function deleteProduct(productId) {
        const product = inventory.find((item) => item.id === productId);
        if (!product) return;

        if (!confirm(`Delete "${product.itemName}" from inventory?`)) return;

        try {
            await api(`/api/products/${productId}`, { method: "DELETE" });
            await loadInventory();
            showMessage("Product deleted successfully.", "success");
        } catch (error) {
            console.error("Delete product error:", error);
            showMessage(error.message, "error");
        }
    }

    // ---------------------------------------------------------
    // SEARCH / FILTERS
    // ---------------------------------------------------------
    $("inventorySearch")?.addEventListener("input", renderInventory);
    $("inventoryType")?.addEventListener("change", renderInventory);
    $("inventoryStatus")?.addEventListener("change", renderInventory);

    // ---------------------------------------------------------
    // PRODUCT DROPDOWNS
    // ---------------------------------------------------------
    function populateProductDropdowns() {
        [$("product"), $("bomProduct")].forEach((select) => {
            if (!select) return;
            const current = select.value;
            const products = inventory.filter((p) =>
                p.type === "Finished Product" || p.type === "Semi Finished Product" || p.type === "Product"
            );
            select.innerHTML = `<option value="">Select a product</option>` + products.map((p) =>
                `<option value="${p.id}">${escapeHtml(p.itemName)}</option>`
            ).join("");
            if (products.some((p) => String(p.id) === current)) select.value = current;
        });
    }

    // ---------------------------------------------------------
    // NOTIFICATIONS
    // ---------------------------------------------------------
    function updateNotifications() {
        const low = inventory.filter((p) => p.status === "Low Stock");
        if ($("notificationCount")) {
            $("notificationCount").textContent = low.length;
            $("notificationCount").style.display = low.length ? "flex" : "none";
        }
        if ($("unreadBadge")) $("unreadBadge").textContent = `${low.length} Unread`;
        if ($("totalNotifications")) $("totalNotifications").textContent = low.length;
        if ($("stockNotifications")) $("stockNotifications").textContent = low.length;
        if ($("productionNotifications")) $("productionNotifications").textContent = 0;
        if ($("orderNotifications")) $("orderNotifications").textContent = 0;

        const feed = $("activityFeed");
        if (!feed) return;
        feed.innerHTML = low.length
            ? `<div class="activity-title">Inventory Alerts</div>` + low.map((p) => `
                <div class="activity-item unread">
                    <div class="activity-item-icon red">!</div>
                    <div class="activity-content">
                        <div class="activity-heading">Low stock: ${escapeHtml(p.itemName)}</div>
                        <p>${formatNumber(p.availableQuantity)} ${escapeHtml(p.unit)} available; minimum is ${formatNumber(p.minimumStock)} ${escapeHtml(p.unit)}.</p>
                        <small>${escapeHtml(p.location)}</small>
                    </div>
                </div>`).join("")
            : `<div class="activity-title">Recent Activity</div><div class="activity-item"><div class="activity-content"><div class="activity-heading">All clear</div><p>No current inventory alerts.</p></div></div>`;
    }

    $("markAllRead")?.addEventListener("click", () => {
        if ($("unreadBadge")) $("unreadBadge").textContent = "0 Unread";
    });

    $("clearNotifications")?.addEventListener("click", () => {
        if ($("activityFeed")) $("activityFeed").innerHTML = `<div class="activity-title">Recent Activity</div><div class="activity-item"><div class="activity-content"><div class="activity-heading">Notifications cleared</div></div></div>`;
    });

    // ---------------------------------------------------------
    // EXPORT
    // ---------------------------------------------------------
    document.querySelectorAll(".export-btn").forEach((button) => {
        button.addEventListener("click", () => {
            if (!inventory.length) {
                showMessage("There is no inventory data to export.", "error");
                return;
            }

            const headers = ["Item Name", "Category", "Type", "Thickness", "Size", "Color", "Available Quantity", "Unit", "Minimum Stock", "Location", "Status"];
            const rows = inventory.map((p) => [
                p.itemName, p.category, p.type, p.thickness, p.sizeDescription, p.color,
                p.availableQuantity, p.unit, p.minimumStock, p.location, p.status
            ]);

            const csv = [headers, ...rows].map((row) =>
                row.map((value) => `"${String(value ?? "").replaceAll('"', '""')}"`).join(",")
            ).join("\n");

            const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = "seon-inventory.csv";
            link.click();
            URL.revokeObjectURL(url);
        });
    });

    // ---------------------------------------------------------
    // INITIAL LOAD
    // ---------------------------------------------------------
    toggleRawFields();
    ensureEditModal();
    loadInventory();
});
