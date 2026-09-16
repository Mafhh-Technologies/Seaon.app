from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError
from app.models.product import Product
from app.schemes.product import ProductCreate


def create_product(db: Session, payload: ProductCreate) -> Product:
	if db.scalar(select(Product).where((Product.name == payload.name) | (Product.sku == payload.sku))):
		raise ConflictError("Product name or SKU already exists")
	product = Product(**payload.model_dump())
	db.add(product)
	db.commit()
	db.refresh(product)
	return product


def list_products(db: Session) -> list[Product]:
	return list(db.scalars(select(Product).order_by(Product.name)))