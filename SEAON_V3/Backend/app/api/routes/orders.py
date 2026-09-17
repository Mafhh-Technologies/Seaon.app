"""
Order routes — CRUD + smart availability check.
"""
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.order import OrderAvailabilityResponse, OrderCreate, OrderOut
from app.services.order_service import OrderService
from app.services.smart_order_service import SmartOrderService

router = APIRouter()


@router.get("", response_model=List[OrderOut])
def list_orders(
    status: str = Query("all"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return OrderService.list_orders(db, status_filter=status)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return OrderService.get_order(db, order_id)


@router.get("/check-availability/{product_id}", response_model=OrderAvailabilityResponse)
def check_availability(
    product_id: int,
    quantity: float = Query(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Frontend calls this as the user types quantity — live material check."""
    return SmartOrderService.check_availability(db, product_id, quantity)


@router.post("", response_model=OrderOut, status_code=201)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    items = [{"product_id": i.product_id, "quantity": i.quantity} for i in payload.items]
    return OrderService.create_order(
        db,
        customer_name=payload.customer_name,
        items=items,
        priority=payload.priority,
        notes=payload.notes,
        user_id=current_user.id,
    )


@router.patch("/{order_id}/status", response_model=OrderOut)
def update_status(
    order_id: int,
    new_status: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return OrderService.update_status(db, order_id, new_status)


@router.delete("/{order_id}", status_code=204)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    OrderService.delete_order(db, order_id)