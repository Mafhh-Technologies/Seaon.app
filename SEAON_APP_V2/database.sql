PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE,
    item_name TEXT NOT NULL,
    category TEXT NOT NULL,
    type TEXT NOT NULL,
    color TEXT,
    thickness TEXT,
    width REAL,
    length_meters REAL,
    size_description TEXT,
    pack_description TEXT,
    available_quantity REAL NOT NULL DEFAULT 0,
    unit TEXT NOT NULL DEFAULT 'Nos',
    minimum_stock REAL NOT NULL DEFAULT 0,
    required_stock REAL NOT NULL DEFAULT 0,
    location TEXT,
    source_file TEXT,
    source_sheet TEXT,
    source_row INTEGER,
    source_date TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    old_quantity REAL NOT NULL,
    new_quantity REAL NOT NULL,
    movement_type TEXT NOT NULL,
    note TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(available_quantity, minimum_stock);
CREATE INDEX IF NOT EXISTS idx_stock_movements_product ON stock_movements(product_id);
