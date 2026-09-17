"""
BOM routes — list / create / delete component mappings.
"""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.inventory import BOMEntryCreate, BOMEntryOut
from app.services.bom_service import BOMService

router = APIRouter()


@router.get("", response_model=List[BOMEntryOut])
def list_bom(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return BOMService.list_all(db)


@router.get("/product/{product_id}", response_model=List[BOMEntryOut])
def list_bom_for_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return BOMService.list_by_product(db, product_id)


@router.post("", response_model=BOMEntryOut, status_code=201)
def create_bom(
    payload: BOMEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return BOMService.create(
        db,
        product_id=payload.product_id,
        component_id=payload.component_id,
        quantity=payload.quantity,
        unit=payload.unit,
    )


@router.delete("/{entry_id}", status_code=204)
def delete_bom(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    BOMService.delete(db, entry_id)