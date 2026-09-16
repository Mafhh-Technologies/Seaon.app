from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.product import BOMItem, Product
from app.schemes.product import BOMCreate


def list_bom(db: Session) -> list[BOMItem]:
	return list(db.scalars(select(BOMItem).order_by(BOMItem.product_id, BOMItem.id)))


def get_product_bom(db: Session, product_name: str) -> list[BOMItem]:
	product = db.scalar(select(Product).where(Product.name == product_name))
	if product is None:
		raise NotFoundError("Product not found")
	return list(db.scalars(select(BOMItem).where(BOMItem.product_id == product.id).order_by(BOMItem.id)))


def create_bom_item(db: Session, payload: BOMCreate) -> BOMItem:
	product = db.scalar(select(Product).where(Product.name == payload.product))
	if product is None:
		product = Product(name=payload.product, sku=payload.product.upper().replace(" ", "-"), unit="pcs")
		db.add(product)
		db.flush()
	if db.scalar(select(BOMItem).where(BOMItem.product_id == product.id, BOMItem.component == payload.component)):
		raise ConflictError("BOM component already exists for this product")
	item = BOMItem(product_id=product.id, component=payload.component, quantity=payload.quantity, unit=payload.unit)
	db.add(item)
	db.commit()
	db.refresh(item)
	return item


def delete_bom_item(db: Session, item_id: int) -> None:
	item = db.get(BOMItem, item_id)
	if item is None:
		raise NotFoundError("BOM item not found")
	db.delete(item)
	db.commit()
