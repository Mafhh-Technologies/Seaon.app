"""
Inventory models — supports FIFO via batches + audit trail via movements.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class MovementType(str, enum.Enum):
    IN = "IN"
    OUT = "OUT"
    ADJUSTMENT = "ADJUSTMENT"
    CONSUMPTION = "CONSUMPTION"
    PRODUCTION = "PRODUCTION"


class InventoryItem(Base):
    """
    Aggregate stock row per product.
    Actual stock is derived from batches, but this row caches the total
    so low-stock checks are a single query.
    """
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), unique=True, nullable=False)
    quantity = Column(Float, nullable=False, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", lazy="joined")

    def __repr__(self) -> str:
        return f"<InventoryItem product={self.product_id} qty={self.quantity}>"


class InventoryBatch(Base):
    """
    A batch of stock for one product.
    FIFO service consumes these oldest-first (by received_at).
    """
    __tablename__ = "inventory_batches"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Float, nullable=False)
    remaining = Column(Float, nullable=False)  # quantity left after FIFO consumption
    unit_cost = Column(Float, nullable=True)
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    batch_code = Column(String(80), nullable=True)

    product = relationship("Product", back_populates="batches")

    def __repr__(self) -> str:
        return f"<Batch id={self.id} product={self.product_id} remaining={self.remaining}>"


class InventoryMovement(Base):
    """Immutable audit log for every stock change."""
    __tablename__ = "inventory_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    movement_type = Column(Enum(MovementType), nullable=False)
    quantity = Column(Float, nullable=False)          # signed
    reference = Column(String(120), nullable=True)    # e.g. "ORDER#12" or "JOB#3"
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)