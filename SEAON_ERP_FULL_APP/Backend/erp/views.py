# API VIEWS: browser requests arrive here, permissions are checked, and services/models are called.
import hashlib,secrets,jwt
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from rest_framework import viewsets
from rest_framework.decorators import action,api_view,permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import *
from .serializers import *
from .authentication import access_token
from .permissions import RolePermission
from .services import create_product,adjust_stock,receive_stock,consume_fifo,stock_health,complete_production

def record_audit(request, action, module, description):
    AuditLog.objects.create(user=request.user, action=action, module=module, description=description)

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
        record_audit(request,"product.created","Products",f"Created {product.name}")
        return Response(ProductSerializer(product).data,status=201)

class InventoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=Inventory.objects.select_related("product").order_by("product__name"); serializer_class=InventorySerializer
    required_permission="inventory.view"
    @action(detail=False,methods=["get"])
    def low_stock(self,request):
        rows=[x for x in self.get_queryset() if x.quantity<=x.product.minimum_stock]
        return Response(self.get_serializer(rows,many=True).data)
    @action(detail=False,methods=["patch"],url_path=r"(?P<product_id>[^/.]+)/stock")
    def stock(self,request,product_id=None):
        self.required_permission="inventory.write"
        try:
            inv=adjust_stock(product_id,float(request.data.get("delta",0)),str(request.data.get("note","")))
            record_audit(request,"stock.adjusted","Inventory",f"Adjusted {inv.product.name} by {request.data.get('delta',0)}")
            return Response(InventorySerializer(inv).data)
        except Exception as e: return Response({"detail":str(e)},status=400)

class OrderViewSet(viewsets.ModelViewSet):
    queryset=Order.objects.select_related("product").order_by("-created_at"); serializer_class=OrderSerializer
    def get_permissions(self):
        self.required_permission="orders.view" if self.action in ("list","retrieve") else "orders.write"; return [RolePermission()]
    def perform_create(self,serializer):
        order=serializer.save(order_number=f"ORD-{secrets.token_hex(5).upper()}")
        record_audit(self.request,"order.created","Orders",f"Created {order.order_number}")
    @action(detail=True,methods=["patch"])
    def complete(self,request,pk=None):
        o=self.get_object(); o.status="completed"; o.save(update_fields=["status"])
        record_audit(request,"order.completed","Orders",f"Completed {o.order_number}")
        return Response(self.get_serializer(o).data)

class ProductionViewSet(viewsets.ModelViewSet):
    queryset=ProductionOrder.objects.select_related("product").order_by("-started_at"); serializer_class=ProductionSerializer
    def get_permissions(self):
        self.required_permission="production.view" if self.action in ("list","retrieve") else "production.write"; return [RolePermission()]
    def perform_create(self,serializer):
        job=serializer.save(production_number=f"PROD-{secrets.token_hex(5).upper()}")
        record_audit(self.request,"production.created","Production",f"Created {job.production_number}")
    @action(detail=True,methods=["post"])
    def complete(self,request,pk=None):
        try:
            p, allocations=complete_production(self.get_object())
        except Exception as e:
            return Response({"detail":str(e)},status=400)
        record_audit(request,"production.completed","Production",f"Completed {p.production_number}")
        return Response({"production":self.get_serializer(p).data,"fifo_allocations":allocations})

class BOMViewSet(viewsets.ModelViewSet):
    queryset=BOMItem.objects.select_related("product","component_product").order_by("product__name"); serializer_class=BOMSerializer
    def perform_create(self,serializer):
        item=serializer.save()
        record_audit(self.request,"bom.created","BOM",f"Added {item.component_product.name} to {item.product.name}")
    def perform_destroy(self,instance):
        record_audit(self.request,"bom.deleted","BOM",f"Removed {instance.component_product.name} from {instance.product.name}")
        instance.delete()
    def get_permissions(self):
        self.required_permission="bom.read" if self.action in ("list","retrieve") else "bom.write"; return [RolePermission()]

@api_view(["GET"])
def health(request): return Response({"ok":True,"service":"SEAON ERP","database":"sqlite"})


@api_view(["GET"])
def dashboard(request):
    """One small endpoint used by the dashboard cards and charts."""
    from django.db.models import Sum
    orders=Order.objects.all()
    production=ProductionOrder.objects.all()
    inventory=Inventory.objects.select_related("product")
    low=[x for x in inventory if x.quantity <= x.product.minimum_stock]
    return Response({
        "orders_total":orders.count(),
        "orders_pending":orders.filter(status__in=["pending","created","approved"]).count(),
        "orders_completed":orders.filter(status="completed").count(),
        "production_active":production.filter(status="in-progress").count(),
        "inventory_items":inventory.count(),
        "low_stock":len(low),
        "stock_units":sum((x.quantity for x in inventory), Decimal("0")),
        "returns_open":ReturnRecord.objects.exclude(status="closed").count(),
        "warehouse_queue":WarehouseTransaction.objects.filter(transaction_type__in=["pick","pack","dispatch"]).count(),
        "fifo_batches":InventoryBatch.objects.filter(remaining_quantity__gt=0).count(),
        "stock_health":stock_health(),
        "recent_orders":Order.objects.select_related("product").order_by("-created_at")[:8].values(
            "id","order_number","customer_name","status","quantity","product__name","created_at"),
    })

@api_view(["GET","POST"])
def batches(request):
    if request.method=="GET":
        if not user_can(request.user,"inventory.fifo"): return Response({"detail":"Permission denied."},status=403)
        return Response(BatchSerializer(InventoryBatch.objects.select_related("product").all()[:1000],many=True).data)
    if not user_can(request.user,"inventory.adjust"): return Response({"detail":"Permission denied."},status=403)
    data=request.data
    try:
        product=Product.objects.get(pk=data.get("product"))
        batch=receive_stock(product,data.get("quantity"),data.get("vendor",""),data.get("batch_code",""),data.get("unit_cost",0),data.get("received_date") or None,data.get("expiry_date") or None,data.get("reference",""))
        record_audit(request,"stock.received","Inventory",f"Received {batch.quantity} {product.unit} of {product.name}")
        return Response(BatchSerializer(batch).data,status=201)
    except Exception as e: return Response({"detail":str(e)},status=400)

@api_view(["POST"])
def fifo_consume(request):
    if not user_can(request.user,"inventory.fifo"): return Response({"detail":"Permission denied."},status=403)
    try:
        product=Product.objects.get(pk=request.data.get("product"))
        allocations=consume_fifo(product,request.data.get("quantity"),request.data.get("reference",""))
        record_audit(request,"fifo.consumed","Inventory",f"FIFO consumed {request.data.get('quantity')} {product.unit} of {product.name}")
        return Response({"ok":True,"allocations":allocations})
    except Exception as e: return Response({"detail":str(e)},status=400)

@api_view(["GET","POST"])
def warehouse(request):
    if request.method=="GET":
        if not user_can(request.user,"inventory.view"): return Response({"detail":"Permission denied."},status=403)
        return Response(WarehouseSerializer(WarehouseTransaction.objects.select_related("product").order_by("-created_at")[:1000],many=True).data)
    if not user_can(request.user,"warehouse.receive"): return Response({"detail":"Permission denied."},status=403)
    try:
        product=Product.objects.get(pk=request.data.get("product"))
        qty=Decimal(str(request.data.get("quantity")))
        kind=str(request.data.get("transaction_type","inward"))
        if kind=="inward":
            receive_stock(product,qty,reference=request.data.get("reference",""))
        else:
            WarehouseTransaction.objects.create(product=product,transaction_type=kind,quantity=qty,reference=request.data.get("reference",""),notes=request.data.get("notes",""))
        record_audit(request,f"warehouse.{kind}","Warehouse",f"{kind.title()} {qty} {product.unit} of {product.name}")
        return Response({"ok":True})
    except Exception as e: return Response({"detail":str(e)},status=400)

@api_view(["GET","POST","PATCH"])
def returns(request,pk=None):
    if request.method=="GET":
        if not user_can(request.user,"returns.view"): return Response({"detail":"Permission denied."},status=403)
        qs=ReturnRecord.objects.select_related("order","order__product").order_by("-created_at")
        return Response(ReturnSerializer(qs,many=True).data)
    if request.method=="POST":
        if not user_can(request.user,"returns.manage"): return Response({"detail":"Permission denied."},status=403)
        try:
            order=Order.objects.get(pk=request.data.get("order"))
            item=ReturnRecord.objects.create(
                order=order,reason=request.data.get("reason",""),
                damage_notes=request.data.get("damage_notes",""),
                photos=request.data.get("photos",""),
                replacement_mode=request.data.get("replacement_mode","replacement"))
            record_audit(request,"return.created","Returns",f"Created return for {order.order_number}")
            return Response(ReturnSerializer(item).data,status=201)
        except Exception as e:return Response({"detail":str(e)},status=400)
    if not user_can(request.user,"returns.manage"): return Response({"detail":"Permission denied."},status=403)
    try:item=ReturnRecord.objects.get(pk=pk)
    except ReturnRecord.DoesNotExist:return Response({"detail":"Return not found."},status=404)
    for key in ["status","damage_notes","replacement_mode","redelivery_status"]:
        if key in request.data:setattr(item,key,request.data[key])
    item.save(); record_audit(request,"return.updated","Returns",f"Updated return #{item.id}")
    return Response(ReturnSerializer(item).data)

@api_view(["GET"])
def reports(request):
    if not user_can(request.user,"reports.view"): return Response({"detail":"Permission denied."},status=403)
    return Response({
        "stock":stock_health(),
        "orders_by_status":{status:Order.objects.filter(status=status).count() for status in ["pending","in-progress","completed","cancelled"]},
        "production_by_status":{status:ProductionOrder.objects.filter(status=status).count() for status in ["in-progress","completed","cancelled"]},
        "returns_by_status":{status:ReturnRecord.objects.filter(status=status).count() for status in ["requested","received","inspection","repair","replacement","redelivery","closed"]},
    })
