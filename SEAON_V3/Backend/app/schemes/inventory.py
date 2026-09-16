from pydantic import BaseModel, ConfigDict, Field


class InventoryBase(BaseModel):
	name: str = Field(min_length=1, max_length=120)
	sku: str = Field(min_length=1, max_length=60)
	quantity: float = Field(ge=0)
	min_stock: float = Field(ge=0, alias="minStock")
	unit: str = Field(min_length=1, max_length=20)

	model_config = ConfigDict(populate_by_name=True)


class InventoryCreate(InventoryBase):
	pass


class StockAdjustment(BaseModel):
	quantity: float


class InventoryRead(InventoryBase):
	model_config = ConfigDict(from_attributes=True, populate_by_name=True)

	id: int
