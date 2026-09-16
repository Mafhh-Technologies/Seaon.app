from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductionCreate(BaseModel):
	product: str = Field(min_length=1)
	quantity: int = Field(gt=0)
	operator: str | None = None


class ProductionComplete(BaseModel):
	output: int = Field(gt=0)


class ProductionRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	product: str
	quantity: int
	status: str
	operator: str | None
	started_at: datetime | None
	completed_at: datetime | None