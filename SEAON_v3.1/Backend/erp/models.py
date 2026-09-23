from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")
    role=models.CharField(max_length=30,default="viewer")
    full_name=models.CharField(max_length=160,blank=True)

class Product(models.Model):
    name=models.CharField(max_length=160)
    sku=models.CharField(max_length=80,unique=True)
    product_type=models.CharField(max_length=30)
    unit=models.CharField(max_length=20,default="pcs")
    minimum_stock=models.DecimalField(max_digits=14,decimal_places=2,default=0)
    location=models.CharField(max_length=120,blank=True)
    thickness=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    size=models.CharField(max_length=80,blank=True)
    color=models.CharField(max_length=80,blank=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)

class Inventory(models.Model):
    product=models.OneToOneField(Product,on_delete=models.CASCADE,related_name="inventory")
    quantity=models.DecimalField(max_digits=14,decimal_places=2,default=0)
    average_cost=models.DecimalField(max_digits=14,decimal_places=2,default=0)
    updated_at=models.DateTimeField(auto_now=True)

class StockMovement(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="movements")
    quantity_change=models.DecimalField(max_digits=14,decimal_places=2)
    quantity_after=models.DecimalField(max_digits=14,decimal_places=2)
    movement_type=models.CharField(max_length=40,default="adjustment")
    note=models.CharField(max_length=255,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    order_number=models.CharField(max_length=50,unique=True)
    customer_name=models.CharField(max_length=160)
    customer_email=models.EmailField(blank=True)
    product=models.ForeignKey(Product,on_delete=models.PROTECT,related_name="orders")
    quantity=models.DecimalField(max_digits=14,decimal_places=2)
    status=models.CharField(max_length=20,default="pending")
    notes=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

class ProductionOrder(models.Model):
    production_number=models.CharField(max_length=50,unique=True)
    product=models.ForeignKey(Product,on_delete=models.PROTECT,related_name="production_orders")
    customer_name=models.CharField(max_length=160,blank=True)
    quantity=models.DecimalField(max_digits=14,decimal_places=2)
    produced_quantity=models.DecimalField(max_digits=14,decimal_places=2,default=0)
    status=models.CharField(max_length=20,default="in-progress")
    assigned_to=models.CharField(max_length=160,blank=True)
    started_at=models.DateTimeField(auto_now_add=True)
    completed_at=models.DateTimeField(null=True,blank=True)

class BOMItem(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="bom_items")
    component_product=models.ForeignKey(Product,on_delete=models.PROTECT,related_name="used_in_boms")
    quantity_per_unit=models.DecimalField(max_digits=14,decimal_places=4)
    unit=models.CharField(max_length=20,default="pcs")
    class Meta:
        constraints=[models.UniqueConstraint(fields=["product","component_product"],name="unique_bom_component")]

class RefreshToken(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="refresh_tokens")
    token_hash=models.CharField(max_length=64,unique=True)
    expires_at=models.DateTimeField()
    revoked=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
