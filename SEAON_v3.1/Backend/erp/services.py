from django.db import transaction
from django.utils import timezone
from .models import Inventory,StockMovement,Product
@transaction.atomic
def create_product(data):
    qty=data.pop("quantity",0)
    product=Product.objects.create(**data)
    Inventory.objects.create(product=product,quantity=qty)
    if qty: StockMovement.objects.create(product=product,quantity_change=qty,quantity_after=qty,movement_type="opening")
    return product
@transaction.atomic
def adjust_stock(product_id,delta,note=""):
    inv=Inventory.objects.select_for_update().get(product_id=product_id)
    new=inv.quantity+delta
    if new<0: raise ValueError("Stock cannot become negative")
    inv.quantity=new; inv.save()
    StockMovement.objects.create(product=inv.product,quantity_change=delta,quantity_after=new,note=note)
    return inv
