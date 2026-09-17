"""
Smart Order Service — validates material availability against the BOM
before allowing an order to be created.
"""
from typing import List

from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem
from app.models.bom import BOMEntry
from app.schemas.order import MaterialAvailability, OrderAvailabilityResponse


class SmartOrderService:
    @staticmethod
    def check_availability(db: Session, product_id: int, quantity: float) -> OrderAvailabilityResponse:
        """
        Given a finished product + quantity, check whether all BOM
        components are available in stock.

        Returns a structured response the UI can render directly.
        """
        bom_entries: List[BOMEntry] = (
            db.query(BOMEntry).filter(BOMEntry.product_id == product_id).all()
        )

        # If no BOM defined, treat as ready (free assembly / non-manufactured)
        if not bom_entries:
            return OrderAvailabilityResponse(order_ready=True, materials=[])

        results: List[MaterialAvailability] = []
        overall_ready = True

        for entry in bom_entries:
            required = entry.quantity * quantity

            inv = (
                db.query(InventoryItem)
                .filter(InventoryItem.product_id == entry.component_id)
                .first()
            )
            available = inv.quantity if inv else 0

            sufficient = available >= required
            shortage = 0 if sufficient else (required - available)

            if not sufficient:
                overall_ready = False

            results.append(MaterialAvailability(
                product_id=entry.component_id,
                product_name=entry.component.name if entry.component else "Unknown",
                required=required,
                available=available,
                sufficient=sufficient,
                shortage=shortage,
            ))

        return OrderAvailabilityResponse(order_ready=overall_ready, materials=results)

    @staticmethod
    def consume_for_order(db: Session, product_id: int, quantity: float, reference: str) -> None:
        """
        Deduct all required components from inventory using FIFO.
        Called after a production order is created.
        """
        from app.services.fifo_service import FIFOService

        bom_entries = db.query(BOMEntry).filter(BOMEntry.product_id == product_id).all()
        for entry in bom_entries:
            required = entry.quantity * quantity
            FIFOService.consume(
                db,
                product_id=entry.component_id,
                quantity=required,
                reference=reference,
                notes=f"Consumed for {product_id} x {quantity}",
            )