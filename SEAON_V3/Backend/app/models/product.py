"""
Product model — both raw materials, semi-finished and finished goods.
Supports the thick/size/colour fields used by tape manufacturing.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, Integer, String
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ProductType(str, enum.Enum):
    RAW_MATERIAL = "Raw Material"
    SEMI_FINISHED = "Semi Finished Product"
    FINISHED = "Finished Product"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    sku = Column(String(80), unique=True, index=True, nullable=False)
    type = Column(Enum(ProductType), nullable=False, default=ProductType.RAW_MATERIAL)

    # Tape-specific attributes (only relevant for raw materials)
    thickness_mm = Column(Float, nullable=True)
    size = Column(String(80), nullable=True)      # e.g. "100x200"
    color = Column(String(60), nullable=True)

    unit = Column(String(20), nullable=False, default="pcs")
    minimum_stock = Column(Float, nullable=False, default=0)
    location = Column(String(120), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    batches = relationship("InventoryBatch", back_populates="product", cascade="all, delete-orphan")
    bom_entries = relationship("BOMEntry", back_populates="component", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Product id={self.id} sku={self.sku} name={self.name}>"