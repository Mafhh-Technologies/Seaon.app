from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
	name: str = Field(min_length=1, max_length=120)
	sku: str = Field(min_length=1, max_length=60)
	unit: str = "pcs"


class BOMCreate(BaseModel):
	product: str = Field(min_length=1)
	component: str = Field(min_length=1)
	quantity: float = Field(gt=0)
	unit: str = Field(min_length=1)


class BOMRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	product: str
	component: str
	quantity: float
	unit: str