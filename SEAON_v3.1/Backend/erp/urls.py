from django.urls import include,path
from rest_framework.routers import DefaultRouter
from .views import *
r=DefaultRouter()
r.register("products",ProductViewSet,basename="products")
r.register("inventory",InventoryViewSet,basename="inventory")
r.register("orders",OrderViewSet,basename="orders")
r.register("production",ProductionViewSet,basename="production")
r.register("bom",BOMViewSet,basename="bom")
urlpatterns=[
 path("auth/login/",login),path("auth/refresh/",refresh),path("auth/logout/",logout),path("auth/me/",me),
 path("health/",health),path("",include(r.urls))]
