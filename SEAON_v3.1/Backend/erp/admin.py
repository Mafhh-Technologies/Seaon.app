from django.contrib import admin
from .models import *
admin.site.register([UserProfile,Product,Inventory,StockMovement,Order,ProductionOrder,BOMItem,RefreshToken])
