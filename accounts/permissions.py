from rest_framework.permissions import BasePermission

class IsVendor(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'VENDOR'
    

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'COSTUMER'
        
