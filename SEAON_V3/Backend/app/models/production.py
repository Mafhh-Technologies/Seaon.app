"""
Production job model — schedules and tracks manufacturing runs.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ProductionStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProductionJob(Base):
    __tablename__ = "production_jobs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    produced_quantity = Column(Float, default=0)
    status = Column(Enum(ProductionStatus), default=ProductionStatus.PENDING, nullable=False)
    operator = Column(String(120), nullable=True)

    scheduled_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    order = relationship("Order", back_populates="production_jobs")
    product = relationship("Product", lazy="joined")

    def __repr__(self) -> str:
        return f"<ProductionJob id={self.id} product={self.product_id} status={self.status.value}>"