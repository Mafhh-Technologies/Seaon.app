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
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
