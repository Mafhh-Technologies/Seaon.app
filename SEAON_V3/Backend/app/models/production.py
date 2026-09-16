from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ProductionJob(Base):
	__tablename__ = "production_jobs"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	product: Mapped[str] = mapped_column(String(120))
	quantity: Mapped[int] = mapped_column(Integer)
	status: Mapped[str] = mapped_column(String(30), default="pending", index=True)
	operator: Mapped[str | None] = mapped_column(String(120), nullable=True)
	started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
	completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
