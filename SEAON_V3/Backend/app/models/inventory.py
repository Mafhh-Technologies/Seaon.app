from datetime import datetime

from sqlalchemy import DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class InventoryItem(Base):
	__tablename__ = "inventory_items"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	name: Mapped[str] = mapped_column(String(120))
	sku: Mapped[str] = mapped_column(String(60), unique=True, index=True)
	quantity: Mapped[float] = mapped_column(Numeric(14, 3), default=0)
	min_stock: Mapped[float] = mapped_column(Numeric(14, 3), default=0)
	unit: Mapped[str] = mapped_column(String(20))
	updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
