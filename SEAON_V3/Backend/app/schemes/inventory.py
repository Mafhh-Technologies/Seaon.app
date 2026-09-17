"""Inventory, product and BOM schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    sku: str = Field(..., min_length=2, max_length=80)
    type: str = "Raw Material"
    thickness_mm: Optional[float] = None
    size: Optional[str] = None
    color: Optional[str] = None
    unit: str = "pcs"
    minimum_stock: float = 0
    location: Optional[str] = None
    initial_quantity: float = 0


class ProductOut(BaseModel):
    id: int
    name: str
    sku: str
    type: str
    thickness_mm: Optional[float]
    size: Optional[str]
    color: Optional[str]
    unit: str
    minimum_stock: float
    location: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class InventoryItemOut(BaseModel):
    id: int
    product_id: int
    product: ProductOut
    quantity: float
    status: str

    model_config = ConfigDict(from_attributes=True)


class StockAdjustment(BaseModel):
    quantity: float = Field(..., description="Signed delta: +10 adds, -5 removes")
    reason: Optional[str] = None


class BOMEntryCreate(BaseModel):
    product_id: int
    component_id: int
    quantity: float = Field(..., gt=0)
    unit: str


class BOMEntryOut(BaseModel):
    id: int
    product_id: int
    component_id: int
    quantity: float
    unit: str

    model_config = ConfigDict(from_attributes=True)