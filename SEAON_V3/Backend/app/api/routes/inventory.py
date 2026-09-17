"""
Inventory routes — products, stock, low-stock alerts.
"""
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.inventory import (
    InventoryItemOut,
    ProductCreate,
    ProductOut,
    StockAdjustment,
)
from app.services.inventory_service import InventoryService

router = APIRouter()


@router.get("", response_model=List[InventoryItemOut])
def list_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return InventoryService.list_inventory(db)


@router.get("/products", response_model=List[ProductOut])
def list_products(
    type: str = Query("all"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return InventoryService.list_products(db, type_filter=type)


@router.post("/products", response_model=ProductOut, status_code=201)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return InventoryService.create_product(db, payload.model_dump())


@router.get("/low-stock", response_model=List[InventoryItemOut])
def low_stock(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return InventoryService.low_stock_items(db)


@router.patch("/{product_id}/stock", response_model=InventoryItemOut)
def adjust_stock(
    product_id: int,
    payload: StockAdjustment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return InventoryService.adjust_stock(db, product_id, payload.quantity, payload.reason)