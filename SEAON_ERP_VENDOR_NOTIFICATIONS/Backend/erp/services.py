# BUSINESS SERVICES: stock changes and other operations live here so views stay simple.
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
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


from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

@transaction.atomic
def receive_stock(product, quantity, vendor="", batch_code="", unit_cost=0, received_date=None, expiry_date=None, reference=""):
    """Receive stock into a new batch and update the live inventory balance."""
    quantity=Decimal(str(quantity))
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")
    received_date=received_date or timezone.localdate()
    batch_code=batch_code or f"BATCH-{timezone.now():%Y%m%d%H%M%S}-{product.id}"
    batch=InventoryBatch.objects.create(
        product=product,batch_code=batch_code,received_date=received_date,
        vendor=vendor,expiry_date=expiry_date,quantity=quantity,
        remaining_quantity=quantity,unit_cost=Decimal(str(unit_cost or 0)))
    inv=Inventory.objects.select_for_update().get(product=product)
    inv.quantity += quantity
    inv.save(update_fields=["quantity","updated_at"])
    StockMovement.objects.create(product=product,quantity_change=quantity,quantity_after=inv.quantity,movement_type="inward",note=reference)
    WarehouseTransaction.objects.create(product=product,transaction_type="inward",quantity=quantity,reference=reference,notes=f"Batch {batch.batch_code}")
    return batch

@transaction.atomic
def consume_fifo(product, quantity, reference=""):
    """Consume the oldest available stock batches first and return the batch allocations."""
    quantity=Decimal(str(quantity))
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")
    inv=Inventory.objects.select_for_update().get(product=product)
    if inv.quantity < quantity:
        raise ValueError(f"Insufficient stock. Available: {inv.quantity}")
    remaining=quantity
    allocations=[]
    batches=InventoryBatch.objects.select_for_update().filter(
        product=product,remaining_quantity__gt=0).order_by("received_date","id")
    for batch in batches:
        if remaining <= 0: break
        used=min(batch.remaining_quantity,remaining)
        batch.remaining_quantity-=used
        batch.save(update_fields=["remaining_quantity"])
        allocations.append({"batch":batch.batch_code,"quantity":str(used),"received_date":str(batch.received_date)})
        remaining-=used
    if remaining>0:
        raise ValueError("FIFO batch records do not contain enough stock.")
    inv.quantity-=quantity
    inv.save(update_fields=["quantity","updated_at"])
    StockMovement.objects.create(product=product,quantity_change=-quantity,quantity_after=inv.quantity,movement_type="fifo-consumption",note=reference)
    WarehouseTransaction.objects.create(product=product,transaction_type="pick",quantity=quantity,reference=reference,notes="FIFO consumption")
    return allocations

def stock_health():
    from .models import Product,Inventory,InventoryBatch
    rows=Inventory.objects.select_related("product")
    low=[x for x in rows if x.quantity <= x.product.minimum_stock]
    dead=[x for x in rows if x.quantity > 0 and not x.product.movements.filter(created_at__gte=timezone.now()-timedelta(days=90)).exists()]
    expiring=InventoryBatch.objects.filter(remaining_quantity__gt=0,expiry_date__isnull=False,expiry_date__lte=timezone.localdate()+timedelta(days=30)).count()
    return {"low_stock":len(low),"dead_stock":len(dead),"near_expiry":expiring}


@transaction.atomic
def complete_production(job):
    """Complete production, consume BOM components by FIFO, then add finished stock."""
    if job.status == "completed":
        return job, []
    allocations=[]
    for item in job.product.bom_items.select_related("component_product").all():
        required=Decimal(str(job.quantity))*Decimal(str(item.quantity_per_unit))
        allocations.append({
            "component": item.component_product.name,
            "quantity": str(required),
            "batches": consume_fifo(item.component_product, required, f"Production {job.production_number}")
        })
    job.status="completed"
    job.produced_quantity=job.quantity
    job.completed_at=timezone.now()
    job.save()
    receive_stock(job.product,job.quantity,vendor="Production",batch_code=f"PROD-{job.production_number}",
                  reference=job.production_number)
    return job, allocations
