"""
BOM service — define and query which components each product needs.
"""
from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.product import Product
from app.models.bom import BOMEntry  # defined below in a tiny module


class BOMService:
    @staticmethod
    def list_all(db: Session) -> List[BOMEntry]:
        return db.query(BOMEntry).all()

    @staticmethod
    def list_by_product(db: Session, product_id: int) -> List[BOMEntry]:
        return db.query(BOMEntry).filter(BOMEntry.product_id == product_id).all()

    @staticmethod
    def create(db: Session, product_id: int, component_id: int, quantity: float, unit: str) -> BOMEntry:
        if product_id == component_id:
            raise ConflictError("A product cannot be its own component.")

        # Ensure both exist
        if not db.query(Product).filter(Product.id == product_id).first():
            raise NotFoundError("Product")
        if not db.query(Product).filter(Product.id == component_id).first():
            raise NotFoundError("Component")

        existing = (
            db.query(BOMEntry)
            .filter(BOMEntry.product_id == product_id, BOMEntry.component_id == component_id)
            .first()
        )
        if existing:
            existing.quantity = quantity
            existing.unit = unit
            db.commit()
            db.refresh(existing)
            return existing

        entry = BOMEntry(
            product_id=product_id,
            component_id=component_id,
            quantity=quantity,
            unit=unit,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def delete(db: Session, entry_id: int) -> None:
        entry = db.query(BOMEntry).filter(BOMEntry.id == entry_id).first()
        if not entry:
            raise NotFoundError("BOM entry")
        db.delete(entry)
        db.commit()