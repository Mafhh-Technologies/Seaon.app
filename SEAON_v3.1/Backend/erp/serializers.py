from rest_framework import serializers
from .models import *
class UserSerializer(serializers.Serializer):
    id=serializers.IntegerField(source="pk")
    email=serializers.EmailField(source="email")
    username=serializers.CharField()
    role=serializers.SerializerMethodField()
    full_name=serializers.SerializerMethodField()
    def get_role(self,o): return getattr(getattr(o,"profile",None),"role","viewer")
    def get_full_name(self,o): return getattr(getattr(o,"profile",None),"full_name","") or o.username
class ProductSerializer(serializers.ModelSerializer):
    quantity=serializers.SerializerMethodField()
    class Meta: model=Product; fields="__all__"
    def get_quantity(self,o): return getattr(getattr(o,"inventory",None),"quantity",0)
class InventorySerializer(serializers.ModelSerializer):
    product_name=serializers.CharField(source="product.name",read_only=True)
    sku=serializers.CharField(source="product.sku",read_only=True)
    minimum_stock=serializers.DecimalField(source="product.minimum_stock",max_digits=14,decimal_places=2,read_only=True)
    unit=serializers.CharField(source="product.unit",read_only=True)
    location=serializers.CharField(source="product.location",read_only=True)
    class Meta:
        model=Inventory
        fields=["id","product","product_name","sku","quantity","minimum_stock","unit","location","average_cost","updated_at"]
class OrderSerializer(serializers.ModelSerializer):
    product_name=serializers.CharField(source="product.name",read_only=True)
    class Meta: model=Order; fields="__all__"; read_only_fields=["order_number","created_at"]
class ProductionSerializer(serializers.ModelSerializer):
    product_name=serializers.CharField(source="product.name",read_only=True)
    class Meta: model=ProductionOrder; fields="__all__"; read_only_fields=["production_number","started_at","completed_at"]
class BOMSerializer(serializers.ModelSerializer):
    product_name=serializers.CharField(source="product.name",read_only=True)
    component_name=serializers.CharField(source="component_product.name",read_only=True)
    class Meta: model=BOMItem; fields="__all__"
