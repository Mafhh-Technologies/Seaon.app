from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import InvalidOperationError, NotFoundError
from app.models.order import Order
from app.schemes.order import OrderCreate


VALID_STATUSES = {"pending", "in-progress", "completed", "cancelled"}


def list_orders(db: Session, page: int = 1, limit: int = 20) -> list[Order]:
	return list(db.scalars(select(Order).order_by(Order.id.desc()).offset((page - 1) * limit).limit(limit)))


def get_order(db: Session, order_id: int) -> Order:
	order = db.get(Order, order_id)
	if order is None:
		raise NotFoundError("Order not found")
	return order


def create_order(db: Session, payload: OrderCreate) -> Order:
	if payload.status not in VALID_STATUSES:
		raise InvalidOperationError("Invalid order status")
	order = Order(order_date=date.today(), **payload.model_dump())
	db.add(order)
	db.commit()
	db.refresh(order)
	return order


def update_order_status(db: Session, order_id: int, status: str) -> Order:
	if status not in VALID_STATUSES:
		raise InvalidOperationError("Invalid order status")
	order = get_order(db, order_id)
	order.status = status
	db.commit()
	db.refresh(order)
	return order


def delete_order(db: Session, order_id: int) -> None:
	order = get_order(db, order_id)
	db.delete(order)
	db.commit()
