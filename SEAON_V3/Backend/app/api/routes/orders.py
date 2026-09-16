from datetime import date

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field


router = APIRouter(prefix="/orders", tags=["orders"])


class Order(BaseModel):
	id: int
	customer: str
	product: str
	quantity: int = Field(gt=0)
	status: str = "pending"
	date: date
	notes: str | None = None


class OrderCreate(BaseModel):
	customer: str = Field(min_length=1)
	product: str = Field(min_length=1)
	quantity: int = Field(gt=0)
	status: str = "pending"
	notes: str | None = None


class StatusUpdate(BaseModel):
	status: str = Field(pattern="^(pending|in-progress|completed|cancelled)$")


_orders = [
	Order(id=1, customer="Acme Corp", product="Widget A", quantity=50, status="pending", date=date(2026, 9, 1)),
	Order(id=2, customer="TechStart Inc", product="Widget B", quantity=30, status="completed", date=date(2026, 8, 28)),
	Order(id=3, customer="GreenLeaf Ltd", product="Widget C", quantity=100, status="in-progress", date=date(2026, 9, 3)),
]


def _find_order(order_id: int) -> Order:
	for order in _orders:
		if order.id == order_id:
			return order
	raise HTTPException(status_code=404, detail="Order not found")


@router.get("", response_model=list[Order])
async def list_orders(page: int = Query(default=1, ge=1), limit: int = Query(default=20, ge=1, le=100)) -> list[Order]:
	start = (page - 1) * limit
	return _orders[start:start + limit]


@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: int) -> Order:
	return _find_order(order_id)


@router.post("", response_model=Order, status_code=201)
async def create_order(payload: OrderCreate) -> Order:
	order = Order(id=max((entry.id for entry in _orders), default=0) + 1, date=date.today(), **payload.model_dump())
	_orders.insert(0, order)
	return order


@router.patch("/{order_id}/status", response_model=Order)
async def update_order_status(order_id: int, payload: StatusUpdate) -> Order:
	order = _find_order(order_id)
	order.status = payload.status
	return order


@router.delete("/{order_id}")
async def delete_order(order_id: int) -> dict[str, str]:
	order = _find_order(order_id)
	_orders.remove(order)
	return {"message": "Order deleted"}
