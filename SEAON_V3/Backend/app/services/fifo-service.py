"""
FIFO service — consume stock oldest-batch-first.

This is the core algorithm that keeps inventory accurate:
when producing an order, we deduct the required raw materials from
batches in the order they were received (First-In, First-Out).
"""
from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import InsufficientStockError
from app.models.inventory import (
    InventoryBatch,
    InventoryItem,
    InventoryMovement,
    MovementType,
)


class FIFOService:
    @staticmethod
    def available_quantity(db: Session, product_id: int) -> float:
        """Total remaining quantity across all un-exhausted batches."""
        total = (
            db.query(InventoryBatch)
            .filter(InventoryBatch.product_id == product_id, InventoryBatch.remaining > 0)
            .with_entities(InventoryBatch.remaining)
            .all()
        )
        return sum(row[0] for row in total)

    @staticmethod
    def consume(
        db: Session,
        product_id: int,
        quantity: float,
        reference: str = "CONSUMPTION",
        notes: str | None = None,
    ) -> List[dict]:
        """
        Consume `quantity` units of `product_id` from oldest batches first.

        Returns a list of {batch_id, consumed} dicts.
        Raises InsufficientStockError if total remaining < quantity.
        """
        if quantity <= 0:
            raise ValueError("Consumption quantity must be positive.")

        batches = (
            db.query(InventoryBatch)
            .filter(InventoryBatch.product_id == product_id, InventoryBatch.remaining > 0)
            .order_by(InventoryBatch.received_at.asc(), InventoryBatch.id.asc())
            .all()
        )

        available = sum(b.remaining for b in batches)
        if available < quantity:
            raise InsufficientStockError(
                f"Not enough stock for product {product_id}. "
                f"Required: {quantity}, Available: {available}"
            )

        remaining_to_consume = quantity
        consumed_log: List[dict] = []

        for batch in batches:
            if remaining_to_consume <= 0:
                break
            take = min(batch.remaining, remaining_to_consume)
            batch.remaining -= take
            remaining_to_consume -= take
            consumed_log.append({"batch_id": batch.id, "consumed": take})

        # Update aggregate inventory row
        inv = db.query(InventoryItem).filter(InventoryItem.product_id == product_id).first()
        if inv:
            inv.quantity = max(0, inv.quantity - quantity)

        # Audit log
        db.add(InventoryMovement(
            product_id=product_id,
            movement_type=MovementType.CONSUMPTION,
            quantity=-quantity,
            reference=reference,
            notes=notes,
        ))
        return consumed_log