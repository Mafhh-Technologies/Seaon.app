from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Product(Base):
	__tablename__ = "products"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
	sku: Mapped[str] = mapped_column(String(60), unique=True, index=True)
	unit: Mapped[str] = mapped_column(String(20), default="pcs")
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
	bom_items: Mapped[list["BOMItem"]] = relationship(back_populates="product", cascade="all, delete-orphan")


class BOMItem(Base):
	__tablename__ = "bom_items"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
	component: Mapped[str] = mapped_column(String(120))
	quantity: Mapped[float] = mapped_column(Numeric(12, 3))
	unit: Mapped[str] = mapped_column(String(20))
	product: Mapped[Product] = relationship(back_populates="bom_items")
