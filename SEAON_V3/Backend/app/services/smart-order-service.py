from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem


@dataclass(frozen=True)
class ReorderSuggestion:
	item_id: int
	sku: str
	name: str
	quantity: float
	reason: str


def get_reorder_suggestions(db: Session) -> list[ReorderSuggestion]:
	items = db.scalars(select(InventoryItem).order_by(InventoryItem.name))
	return [
		ReorderSuggestion(
			item_id=item.id,
			sku=item.sku,
			name=item.name,
			quantity=max(float(item.min_stock) - float(item.quantity), 0),
			reason="Quantity is at or below minimum stock",
		)
		for item in items
		if float(item.quantity) <= float(item.min_stock)
	]
