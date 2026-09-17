"""
Inventory service — CRUD for products, stock adjustments, low-stock queries.
"""
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.inventory import (
    InventoryBatch,
    InventoryItem,
    InventoryMovement,
    MovementType,
)
from app.models.product import Product, ProductType


class InventoryService:
    # ── Products ───────────────────────────────────────────────────────────
    @staticmethod
    def list_products(db: Session, type_filter: Optional[str] = None) -> List[Product]:
        query = db.query(Product)
        if type_filter and type_filter != "all":
            query = query.filter(Product.type == ProductType(type_filter))
        return query.order_by(Product.name).all()

    @staticmethod
    def get_product(db: Session, product_id: int) -> Product:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise NotFoundError("Product")
        return product

    @staticmethod
    def create_product(db: Session, data: dict) -> Product:
        if db.query(Product).filter(Product.sku == data["sku"]).first():
            raise ConflictError(f"SKU '{data['sku']}' already exists")

        initial_qty = data.pop("initial_quantity", 0)
        product = Product(
            **data,
            type=ProductType(data.get("type", "Raw Material")),
        )
        db.add(product)
        db.flush()

        # Create aggregate inventory row
        inv = InventoryItem(product_id=product.id, quantity=initial_qty)
        db.add(inv)

        # Create opening batch for FIFO
        if initial_qty > 0:
            db.add(InventoryBatch(
                product_id=product.id,
                quantity=initial_qty,
                remaining=initial_qty,
                batch_code=f"OPEN-{product.sku}",
            ))
            db.add(InventoryMovement(
                product_id=product.id,
                movement_type=MovementType.IN,
                quantity=initial_qty,
                reference="OPENING",
                notes="Initial stock on product creation",
            ))

        db.commit()
        db.refresh(product)
        return product

    # ── Listings ───────────────────────────────────────────────────────────
    @staticmethod
    def list_inventory(db: Session) -> List[dict]:
        rows = (
            db.query(InventoryItem, Product)
            .join(Product, Product.id == InventoryItem.product_id)
            .all()
        )
        result = []
        for inv, prod in rows:
            status = "Low Stock" if inv.quantity < prod.minimum_stock else "OK"
            result.append({
                "id": inv.id,
                "product_id": prod.id,
                "product": prod,
                "quantity": inv.quantity,
                "status": status,
            })
        return result

    @staticmethod
    def low_stock_items(db: Session) -> List[dict]:
        return [row for row in InventoryService.list_inventory(db) if row["status"] == "Low Stock"]

    # ── Adjustments ────────────────────────────────────────────────────────
    @staticmethod
    def adjust_stock(db: Session, product_id: int, delta: float, reason: Optional[str] = None) -> InventoryItem:
        product = InventoryService.get_product(db, product_id)
        inv = db.query(InventoryItem).filter(InventoryItem.product_id == product_id).first()
        if not inv:
            inv = InventoryItem(product_id=product_id, quantity=0)
            db.add(inv)
            db.flush()

        if delta < 0:
            # Route negatives through FIFO so batches stay consistent
            from app.services.fifo_service import FIFOService
            FIFOService.consume(db, product_id, abs(delta), reference="ADJUSTMENT")
        else:
            # Positive delta creates a new batch
            db.add(InventoryBatch(
                product_id=product_id,
                quantity=delta,
                remaining=delta,
                batch_code=f"ADJ-{product.sku}",
            ))
            inv.quantity += delta

        db.add(InventoryMovement(
            product_id=product_id,
            movement_type=MovementType.ADJUSTMENT,
            quantity=delta,
            reference="MANUAL",
            notes=reason or "Manual adjustment",
        ))
        db.commit()
        db.refresh(inv)
        return inv