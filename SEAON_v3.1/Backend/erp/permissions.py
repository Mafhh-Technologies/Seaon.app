from rest_framework.permissions import BasePermission
ROLES={
 "super-admin":{"*"},
 "admin":{"products.read","products.write","inventory.read","inventory.write","orders.read","orders.write","production.read","production.write","bom.read","bom.write"},
 "manager":{"products.read","inventory.read","inventory.write","orders.read","orders.write","production.read","production.write","bom.read","bom.write"},
 "operator":{"products.read","inventory.read","production.read","production.write","bom.read"},
 "viewer":{"products.read","inventory.read","orders.read","production.read","bom.read"}}
class RolePermission(BasePermission):
    def has_permission(self,request,view):
        if not request.user or not request.user.is_authenticated:return False
        perm=getattr(view,"required_permission",None)
        role=getattr(getattr(request.user,"profile",None),"role","viewer")
        return not perm or "*" in ROLES.get(role,set()) or perm in ROLES.get(role,set())
