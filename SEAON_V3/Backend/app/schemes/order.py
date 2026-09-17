"""Order schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: float = Field(..., gt=0)


class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=200)
    items: List[OrderItemCreate] = Field(..., min_length=1)
    priority: str = "medium"
    notes: Optional[str] = None


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    quantity: float
    unit_price: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class OrderOut(BaseModel):
    id: int
    customer_name: str
    status: str
    priority: str
    notes: Optional[str]
    created_at: datetime
    items: List[OrderItemOut] = []

    model_config = ConfigDict(from_attributes=True)


class MaterialAvailability(BaseModel):
    product_id: int
    product_name: str
    required: float
    available: float
    sufficient: bool
    shortage: float = 0


class OrderAvailabilityResponse(BaseModel):
    order_ready: bool
    materials: List[MaterialAvailability]