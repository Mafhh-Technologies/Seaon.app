from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field


router = APIRouter(prefix="/inventory", tags=["inventory"])


class InventoryItem(BaseModel):
	id: int
	name: str
	sku: str
	quantity: float = Field(ge=0)
	minStock: float = Field(ge=0)
	unit: str


class InventoryCreate(BaseModel):
	name: str = Field(min_length=1)
	sku: str = Field(min_length=1)
	quantity: float = Field(ge=0)
	minStock: float = Field(ge=0)
	unit: str = Field(min_length=1)


class StockUpdate(BaseModel):
	quantity: float


_items = [
	InventoryItem(id=1, name="Raw Material X", sku="RM-001", quantity=500, minStock=50, unit="kg"),
	InventoryItem(id=2, name="Raw Material Y", sku="RM-002", quantity=120, minStock=30, unit="kg"),
	InventoryItem(id=3, name="Component A", sku="CMP-001", quantity=250, minStock=20, unit="pcs"),
	InventoryItem(id=4, name="Component B", sku="CMP-002", quantity=45, minStock=50, unit="pcs"),
	InventoryItem(id=5, name="Finished Product Z", sku="FP-001", quantity=80, minStock=10, unit="pcs"),
]


def _find_item(item_id: int) -> InventoryItem:
	for item in _items:
		if item.id == item_id:
			return item
	raise HTTPException(status_code=404, detail="Inventory item not found")


@router.get("", response_model=list[InventoryItem])
async def list_inventory() -> list[InventoryItem]:
	return _items


@router.get("/low-stock", response_model=list[InventoryItem])
async def low_stock(threshold: float = Query(default=10, ge=0)) -> list[InventoryItem]:
	return [item for item in _items if item.quantity <= max(item.minStock, threshold)]


@router.get("/{item_id}", response_model=InventoryItem)
async def get_inventory_item(item_id: int) -> InventoryItem:
	return _find_item(item_id)


@router.post("", response_model=InventoryItem, status_code=201)
async def create_inventory_item(payload: InventoryCreate) -> InventoryItem:
	if any(item.sku.lower() == payload.sku.lower() for item in _items):
		raise HTTPException(status_code=409, detail="SKU already exists")
	item = InventoryItem(id=max((entry.id for entry in _items), default=0) + 1, **payload.model_dump())
	_items.append(item)
	return item


@router.patch("/{item_id}/stock", response_model=InventoryItem)
async def update_stock(item_id: int, payload: StockUpdate) -> InventoryItem:
	item = _find_item(item_id)
	new_quantity = item.quantity + payload.quantity
	if new_quantity < 0:
		raise HTTPException(status_code=400, detail="Stock cannot become negative")
	item.quantity = new_quantity
	return item


@router.delete("/{item_id}")
async def delete_inventory_item(item_id: int) -> dict[str, str]:
	item = _find_item(item_id)
	_items.remove(item)
	return {"message": "Inventory item deleted"}
