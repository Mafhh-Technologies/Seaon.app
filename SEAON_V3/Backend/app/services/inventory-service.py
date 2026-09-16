from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, InvalidOperationError, NotFoundError
from app.models.inventory import InventoryItem
from app.schemes.inventory import InventoryCreate


def list_inventory(db: Session) -> list[InventoryItem]:
	return list(db.scalars(select(InventoryItem).order_by(InventoryItem.name)))


def get_inventory_item(db: Session, item_id: int) -> InventoryItem:
	item = db.get(InventoryItem, item_id)
	if item is None:
		raise NotFoundError("Inventory item not found")
	return item


def create_inventory_item(db: Session, payload: InventoryCreate) -> InventoryItem:
	if db.scalar(select(InventoryItem).where(InventoryItem.sku == payload.sku)):
		raise ConflictError("SKU already exists")
	item = InventoryItem(**payload.model_dump(by_alias=False))
	db.add(item)
	db.commit()
	db.refresh(item)
	return item


def adjust_stock(db: Session, item_id: int, change: float) -> InventoryItem:
	item = get_inventory_item(db, item_id)
	if float(item.quantity) + change < 0:
		raise InvalidOperationError("Stock cannot become negative")
	item.quantity = float(item.quantity) + change
	db.commit()
	db.refresh(item)
	return item


def delete_inventory_item(db: Session, item_id: int) -> None:
	item = get_inventory_item(db, item_id)
	db.delete(item)
	db.commit()
