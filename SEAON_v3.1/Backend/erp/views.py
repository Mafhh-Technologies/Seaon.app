import hashlib,secrets,jwt
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action,api_view,permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import *
from .serializers import *
from .authentication import access_token
from .permissions import RolePermission
from .services import create_product,adjust_stock

def user_data(user): return UserSerializer(user).data

@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    email=str(request.data.get("email","")).strip()
    password=str(request.data.get("password",""))
    user=User.objects.filter(email__iexact=email).first()
    if not user or not authenticate(username=user.username,password=password):
        return Response({"detail":"Invalid email or password."},status=401)
    refresh=jwt.encode({"sub":user.pk,"type":"refresh","exp":timezone.now()+timedelta(days=14)},settings.SECRET_KEY,algorithm="HS256")
    RefreshToken.objects.create(user=user,token_hash=hashlib.sha256(refresh.encode()).hexdigest(),expires_at=timezone.now()+timedelta(days=14))
    return Response({"access":access_token(user),"refresh":refresh,"user":user_data(user)})

@api_view(["POST"])
@permission_classes([AllowAny])
def refresh(request):
    raw=request.data.get("refresh","")
    try:
        d=jwt.decode(raw,settings.SECRET_KEY,algorithms=["HS256"])
        if d.get("type")!="refresh": raise ValueError()
        h=hashlib.sha256(raw.encode()).hexdigest()
        rt=RefreshToken.objects.get(token_hash=h,revoked=False,expires_at__gt=timezone.now())
        return Response({"access":access_token(rt.user)})
    except Exception: return Response({"detail":"Invalid or expired refresh token."},status=401)

@api_view(["POST"])
def logout(request):
    RefreshToken.objects.filter(user=request.user,revoked=False).update(revoked=True)
    return Response({"ok":True})

@api_view(["GET"])
def me(request): return Response(user_data(request.user))

class ProductViewSet(viewsets.ModelViewSet):
    queryset=Product.objects.all().order_by("name"); serializer_class=ProductSerializer
    def get_permissions(self):
        self.required_permission="products.read" if self.action in ("list","retrieve") else "products.write"; return [RolePermission()]
    def create(self,request,*a,**k):
        data=request.data.copy()
        for key in ("minimum_stock","quantity","thickness"):
            if key in data and data[key]=="": data[key]=0
        product=create_product(dict(data))
        return Response(ProductSerializer(product).data,status=201)

class InventoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=Inventory.objects.select_related("product").order_by("product__name"); serializer_class=InventorySerializer
    required_permission="inventory.read"
    @action(detail=False,methods=["get"])
    def low_stock(self,request):
        rows=[x for x in self.get_queryset() if x.quantity<=x.product.minimum_stock]
        return Response(self.get_serializer(rows,many=True).data)
    @action(detail=False,methods=["patch"],url_path=r"(?P<product_id>[^/.]+)/stock")
    def stock(self,request,product_id=None):
        self.required_permission="inventory.write"
        try: return Response(InventorySerializer(adjust_stock(product_id,float(request.data.get("delta",0)),str(request.data.get("note","")))).data)
        except Exception as e: return Response({"detail":str(e)},status=400)

class OrderViewSet(viewsets.ModelViewSet):
    queryset=Order.objects.select_related("product").order_by("-created_at"); serializer_class=OrderSerializer
    def get_permissions(self):
        self.required_permission="orders.read" if self.action in ("list","retrieve") else "orders.write"; return [RolePermission()]
    def perform_create(self,serializer): serializer.save(order_number=f"ORD-{secrets.token_hex(5).upper()}")
    @action(detail=True,methods=["patch"])
    def complete(self,request,pk=None):
        o=self.get_object(); o.status="completed"; o.save(update_fields=["status"]); return Response(self.get_serializer(o).data)

class ProductionViewSet(viewsets.ModelViewSet):
    queryset=ProductionOrder.objects.select_related("product").order_by("-started_at"); serializer_class=ProductionSerializer
    def get_permissions(self):
        self.required_permission="production.read" if self.action in ("list","retrieve") else "production.write"; return [RolePermission()]
    def perform_create(self,serializer): serializer.save(production_number=f"PROD-{secrets.token_hex(5).upper()}")
    @action(detail=True,methods=["post"])
    def complete(self,request,pk=None):
        p=self.get_object(); p.status="completed"; p.produced_quantity=p.quantity; p.completed_at=timezone.now(); p.save()
        try: adjust_stock(p.product_id,float(p.quantity),"Production completed")
        except Exception: pass
        return Response(self.get_serializer(p).data)

class BOMViewSet(viewsets.ModelViewSet):
    queryset=BOMItem.objects.select_related("product","component_product").order_by("product__name"); serializer_class=BOMSerializer
    def get_permissions(self):
        self.required_permission="bom.read" if self.action in ("list","retrieve") else "bom.write"; return [RolePermission()]

@api_view(["GET"])
def health(request): return Response({"ok":True,"service":"SEAON ERP","database":"sqlite"})
