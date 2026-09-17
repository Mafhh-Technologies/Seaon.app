from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Order(Base):
	__tablename__ = "orders"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	customer: Mapped[str] = mapped_column(String(160))
	product: Mapped[str] = mapped_column(String(120))
	quantity: Mapped[int] = mapped_column(Integer)
	status: Mapped[str] = mapped_column(String(30), default="pending", index=True)
	order_date: Mapped[date] = mapped_column(Date, default=date.today)
	notes: Mapped[str | None] = mapped_column(Text, nullable=True)
	created_at: Mapped[datetim"""
Order model — customer orders with line items and status workflow.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(200), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    notes = Column(Text, nullable=True)
    priority = Column(String(20), default="medium")  # low | medium | high

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    created_by_user = relationship("User", back_populates="orders")
    production_jobs = relationship("ProductionJob", back_populates="order", cascade="all, delete-orphan")

    @property
    def total_quantity(self) -> float:
        return sum(item.quantity for item in self.items)

    def __repr__(self) -> str:
        return f"<Order id={self.id} customer={self.customer_name} status={self.status.value}>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=True)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", lazy="joined")

    def __repr__(self) -> str:
        return f"<OrderItem order={self.order_id} product={self.product_id} qty={self.quantity}>"e] = mapped_column(DateTime(timezone=True), server_default=func.now())
