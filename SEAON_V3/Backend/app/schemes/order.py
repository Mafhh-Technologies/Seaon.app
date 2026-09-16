from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class OrderCreate(BaseModel):
	customer: str = Field(min_length=1, max_length=160)
	product: str = Field(min_length=1, max_length=120)
	quantity: int = Field(gt=0)
	status: str = "pending"
	notes: str | None = None


class OrderStatusUpdate(BaseModel):
	status: str = Field(pattern="^(pending|in-progress|completed|cancelled)$")


class OrderRead(BaseModel):
	model_config = ConfigDict(from_attributes=True, populate_by_name=True)

	id: int
	customer: str
	product: str
	quantity: int
	status: str
	date: date = Field(validation_alias="order_date", serialization_alias="date")
	notes: str | None = None
