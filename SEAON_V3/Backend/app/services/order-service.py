"""
Order service — create orders (with availability check), update status, list.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.order import Order, OrderItem, OrderStatus
from app.models.inventory import InventoryItem
from app.services.smart_order_service import SmartOrderService


class OrderService:
    @staticmethod
    def list_orders(db: Session, status_filter: Optional[str] = None) -> List[Order]:
        q = db.query(Order)
        if status_filter and status_filter != "all":
            q = q.filter(Order.status == OrderStatus(status_filter))
        return q.order_by(Order.created_at.desc()).all()

    @staticmethod
    def get_order(db: Session, order_id: int) -> Order:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise NotFoundError("Order")
        return order

    @staticmethod
    def create_order(db: Session, customer_name: str, items: list, priority: str = "medium",
                     notes: Optional[str] = None, user_id: Optional[int] = None) -> Order:
        if not items:
            raise ConflictError("Order must contain at least one item.")

        # Build order header first
        order = Order(
            customer_name=customer_name,
            status=OrderStatus.PENDING,
            priority=priority,
            notes=notes,
            created_by=user_id,
        )
        db.add(order)
        db.flush()  # gives us order.id

        # Validate every line item against BOM availability before saving
        for item in items:
            availability = SmartOrderService.check_availability(db, item["product_id"], item["quantity"])
            if not availability.order_ready:
                db.rollback()
                shortage_desc = ", ".join(
                    f"{m.product_name} (short {m.shortage})"
                    for m in availability.materials if not m.sufficient
                )
                raise ConflictError(f"Insufficient materials: {shortage_desc}")

            db.add(OrderItem(
                order_id=order.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
            ))

        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def update_status(db: Session, order_id: int, new_status: str) -> Order:
        order = OrderService.get_order(db, order_id)
        order.status = OrderStatus(new_status)

        # When moving to in-progress, consume raw materials via FIFO
        if new_status == OrderStatus.IN_PROGRESS.value:
            for item in order.items:
                SmartOrderService.consume_for_order(
                    db,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    reference=f"ORDER#{order.id}",
                )

        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def delete_order(db: Session, order_id: int) -> None:
        order = OrderService.get_order(db, order_id)
        db.delete(order)
        db.commit()