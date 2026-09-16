from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(prefix="/bom", tags=["bom"])


class BOMItem(BaseModel):
	id: int
	product: str
	component: str
	quantity: float = Field(gt=0)
	unit: str


class BOMCreate(BaseModel):
	product: str = Field(min_length=1)
	component: str = Field(min_length=1)
	quantity: float = Field(gt=0)
	unit: str = Field(min_length=1)


_bom = [
	BOMItem(id=1, product="Widget A", component="Raw Material X", quantity=2, unit="kg"),
	BOMItem(id=2, product="Widget A", component="Component A", quantity=4, unit="pcs"),
	BOMItem(id=3, product="Widget B", component="Raw Material Y", quantity=3, unit="kg"),
	BOMItem(id=4, product="Widget B", component="Component B", quantity=2, unit="pcs"),
	BOMItem(id=5, product="Widget C", component="Raw Material X", quantity=1, unit="kg"),
	BOMItem(id=6, product="Widget C", component="Component A", quantity=6, unit="pcs"),
]


@router.get("", response_model=list[BOMItem])
async def list_bom() -> list[BOMItem]:
	return _bom


@router.get("/product/{product_id}", response_model=list[BOMItem])
async def get_product_bom(product_id: str) -> list[BOMItem]:
	items = [item for item in _bom if item.product.lower() == product_id.lower()]
	if not items:
		raise HTTPException(status_code=404, detail="BOM not found for product")
	return items


@router.post("", response_model=BOMItem, status_code=201)
async def create_bom_item(payload: BOMCreate) -> BOMItem:
	item = BOMItem(id=max((entry.id for entry in _bom), default=0) + 1, **payload.model_dump())
	_bom.append(item)
	return item
