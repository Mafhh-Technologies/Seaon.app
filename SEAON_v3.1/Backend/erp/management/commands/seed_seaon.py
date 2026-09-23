from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from erp.models import *
class Command(BaseCommand):
    def handle(self,*a,**k):
        u,_=User.objects.get_or_create(username="admin@seaon.com",defaults={"email":"admin@seaon.com"})
        u.email="admin@seaon.com"; u.set_password("Admin@123"); u.save()
        p,_=UserProfile.objects.get_or_create(user=u); p.role="super-admin"; p.full_name="SEAON Administrator"; p.save()
        seed=[
         ("Raw Material X","RM-001","raw-material","kg",50,500),
         ("Raw Material Y","RM-002","raw-material","kg",30,120),
         ("Component A","CMP-001","component","pcs",20,250),
         ("Component B","CMP-002","component","pcs",50,45),
         ("Widget A","WID-A","finished","pcs",20,80),
         ("Widget B","WID-B","finished","pcs",20,60),
         ("Widget C","WID-C","finished","pcs",15,30)]
        ps={}
        for n,sku,t,u,m,q in seed:
            x,_=Product.objects.update_or_create(sku=sku,defaults={"name":n,"product_type":t,"unit":u,"minimum_stock":m,"location":"Main Store"})
            Inventory.objects.update_or_create(product=x,defaults={"quantity":q}); ps[sku]=x
        for a,b,q,u in [("WID-A","RM-001",2,"kg"),("WID-A","CMP-001",4,"pcs"),("WID-B","RM-002",3,"kg"),("WID-B","CMP-002",2,"pcs"),("WID-C","RM-001",1,"kg"),("WID-C","CMP-001",6,"pcs")]:
            BOMItem.objects.update_or_create(product=ps[a],component_product=ps[b],defaults={"quantity_per_unit":q,"unit":u})
        self.stdout.write(self.style.SUCCESS("SEAON demo data ready."))
