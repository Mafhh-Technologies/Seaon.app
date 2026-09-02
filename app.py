from flask import Flask, jsonify, render_template, request
from database import get_db, init_db
import sqlite3

app = Flask(__name__)

# STARTUP
init_db()

@app.after_request
def add_no_cache_headers(response):
    # Prevent the browser from keeping an old JS/HTML copy while developing.
    response.headers["Cache-Control"] = "no-store"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.get("/api/health")
def health():
    connection = get_db()
    count = connection.execute("SELECT COUNT(*) AS total FROM products").fetchone()["total"]
    connection.close()
    return jsonify({"status": "ok", "database": "connected", "products": count})

def product_to_dict(row):
    available = float(row["available_quantity"] or 0)
    minimum = float(row["minimum_stock"] or 0)
    return {
        "id": row["id"],
        "sku": row["sku"],
        "itemName": row["item_name"],
        "category": row["category"],
        "type": row["type"],
        "color": row["color"] or "",
        "thickness": row["thickness"] or "",
        "width": row["width"],
        "lengthMeters": row["length_meters"],
        "sizeDescription": row["size_description"] or "",
        "packDescription": row["pack_description"] or "",
        "availableQuantity": available,
        "unit": row["unit"],
        "minimumStock": minimum,
        "requiredStock": float(row["required_stock"] or 0),
        "location": row["location"] or "",
        "sourceFile": row["source_file"] or "",
        "sourceSheet": row["source_sheet"] or "",
        "sourceRow": row["source_row"],
        "sourceDate": row["source_date"] or "",
        "status": "Low Stock" if minimum > 0 and available <= minimum else "OK",
    }


def read_product_payload(data):
    if not isinstance(data, dict):
        raise ValueError("Request body must be JSON.")

    item_name = str(data.get("itemName", "")).strip()
    category = str(data.get("category", "General")).strip() or "General"
    product_type = str(data.get("type", "")).strip()
    unit = str(data.get("unit", "")).strip()
    location = str(data.get("location", "")).strip()

    if not item_name:
        raise ValueError("Item Name is required.")
    if not product_type:
        raise ValueError("Type is required.")
    if not unit:
        raise ValueError("Unit is required.")
    if not location:
        raise ValueError("Location is required.")

    try:
        available = float(data.get("availableQuantity", 0))
        minimum = float(data.get("minimumStock", 0))
    except (TypeError, ValueError):
        raise ValueError("Available Quantity and Minimum Stock must be numbers.")

    if available < 0 or minimum < 0:
        raise ValueError("Quantity cannot be negative.")

    def optional_number(key):
        value = data.get(key)
        if value in (None, ""):
            return None
        try:
            number = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{key} must be a number.")
        if number < 0:
            raise ValueError(f"{key} cannot be negative.")
        return number

    return {
        "item_name": item_name,
        "category": category,
        "type": product_type,
        "color": str(data.get("color", "")).strip() or None,
        "thickness": str(data.get("thickness", "")).strip() or None,
        "width": optional_number("width"),
        "length_meters": optional_number("lengthMeters"),
        "size_description": str(data.get("sizeDescription", data.get("size", ""))).strip() or None,
        "pack_description": str(data.get("packDescription", "")).strip() or None,
        "available_quantity": available,
        "unit": unit,
        "minimum_stock": minimum,
        "required_stock": max(minimum - available, 0),
        "location": location,
        "sku": str(data.get("sku", "")).strip() or None,
    }

@app.get("/api/products")
def get_products():
    connection = get_db()
    rows = connection.execute(
        "SELECT * FROM products ORDER BY id DESC"
    ).fetchall()
    connection.close()
    return jsonify([product_to_dict(row) for row in rows])

@app.post("/api/products")
def create_product():
    try:
        payload = read_product_payload(request.get_json(silent=True))
        connection = get_db()

        # SKU is optional. If the user supplies one, it must be unique.
        cursor = connection.execute(
            """
            INSERT INTO products (
                sku, item_name, category, type, color, thickness,
                width, length_meters, size_description, pack_description,
                available_quantity, unit, minimum_stock, required_stock, location
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["sku"],
                payload["item_name"],
                payload["category"],
                payload["type"],
                payload["color"],
                payload["thickness"],
                payload["width"],
                payload["length_meters"],
                payload["size_description"],
                payload["pack_description"],
                payload["available_quantity"],
                payload["unit"],
                payload["minimum_stock"],
                payload["required_stock"],
                payload["location"],
            ),
        )
        product_id = cursor.lastrowid
        connection.commit()
        connection.close()
        return jsonify({"message": "Product added successfully.", "id": product_id}), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except sqlite3.IntegrityError as error:
        return jsonify({"error": "Database error: SKU already exists or violates a database rule."}), 409
    except sqlite3.Error as error:
        app.logger.exception("Database error while adding product")
        return jsonify({"error": f"Database error: {error}"}), 500

@app.put("/api/products/<int:product_id>")
def update_product(product_id):
    try:
        payload = read_product_payload(request.get_json(silent=True))
        connection = get_db()
        existing = connection.execute(
            "SELECT id FROM products WHERE id = ?", (product_id,)
        ).fetchone()

        if existing is None:
            connection.close()
            return jsonify({"error": "Product not found."}), 404

        connection.execute(
            """
            UPDATE products SET
                sku=?, item_name=?, category=?, type=?, color=?, thickness=?,
                width=?, length_meters=?, size_description=?, pack_description=?,
                available_quantity=?, unit=?, minimum_stock=?, required_stock=?,
                location=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (
                payload["sku"], payload["item_name"], payload["category"],
                payload["type"], payload["color"], payload["thickness"],
                payload["width"], payload["length_meters"],
                payload["size_description"], payload["pack_description"],
                payload["available_quantity"], payload["unit"],
                payload["minimum_stock"], payload["required_stock"],
                payload["location"], product_id,
            ),
        )
        connection.commit()
        connection.close()
        return jsonify({"message": "Product updated successfully."})

    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except sqlite3.IntegrityError:
        return jsonify({"error": "Database error: SKU already exists."}), 409
    except sqlite3.Error as error:
        app.logger.exception("Database error while updating product")
        return jsonify({"error": f"Database error: {error}"}), 500


@app.patch("/api/products/<int:product_id>/stock")
def adjust_stock(product_id):
    data = request.get_json(silent=True) or {}
    try:
        new_quantity = float(data.get("availableQuantity"))
    except (TypeError, ValueError):
        return jsonify({"error": "New Quantity must be a number."}), 400

    if new_quantity < 0:
        return jsonify({"error": "Quantity cannot be negative."}), 400

    connection = get_db()
    row = connection.execute(
        "SELECT available_quantity FROM products WHERE id = ?", (product_id,)
    ).fetchone()

    if row is None:
        connection.close()
        return jsonify({"error": "Product not found."}), 404

    old_quantity = float(row["available_quantity"] or 0)
    note = str(data.get("note", "Manual stock adjustment")).strip() or "Manual stock adjustment"

    connection.execute(
        """
        UPDATE products
        SET available_quantity=?,
            required_stock=MAX(minimum_stock-?, 0),
            updated_at=CURRENT_TIMESTAMP
        WHERE id=?
        """,
        (new_quantity, new_quantity, product_id),
    )

    connection.execute(
        """
        INSERT INTO stock_movements
            (product_id, old_quantity, new_quantity, movement_type, note)
        VALUES (?, ?, ?, ?, ?)
        """,
        (product_id, old_quantity, new_quantity, "ADJUST", note),
    )

    connection.commit()
    connection.close()
    return jsonify({"message": "Stock adjusted successfully."})


@app.get("/api/products/<int:product_id>/movements")
def get_stock_movements(product_id):
    connection = get_db()
    rows = connection.execute(
        """
        SELECT id, old_quantity, new_quantity, movement_type, note, created_at
        FROM stock_movements
        WHERE product_id=?
        ORDER BY id DESC
        """,
        (product_id,),
    ).fetchall()
    connection.close()
    return jsonify([dict(row) for row in rows])


@app.delete("/api/products/<int:product_id>")
def delete_product(product_id):
    connection = get_db()
    cursor = connection.execute("DELETE FROM products WHERE id=?", (product_id,))

    if cursor.rowcount == 0:
        connection.close()
        return jsonify({"error": "Product not found."}), 404

    connection.commit()
    connection.close()
    return jsonify({"message": "Product deleted successfully."})


@app.get("/api/stats")
def stats():
    connection = get_db()
    row = connection.execute(
        """
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN minimum_stock > 0 AND available_quantity <= minimum_stock THEN 1 ELSE 0 END) AS low,
            SUM(CASE WHEN minimum_stock <= 0 OR available_quantity > minimum_stock THEN 1 ELSE 0 END) AS ok
        FROM products
        """
    ).fetchone()
    connection.close()
    return jsonify({
        "total": row["total"] or 0,
        "low": row["low"] or 0,
        "ok": row["ok"] or 0,
    })

if __name__ == "__main__":
    print("SEON ERP server running at http://127.0.0.1:5000")
    print(f"Database: {app.root_path}/database.db")
    app.run(host="127.0.0.1", port=5000, debug=True)