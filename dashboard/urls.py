from django.urls import path
from .views import CustomerDashboardView, VendorDashboardView, AdminDashboardView

urlpatterns = [
    path('customer/', CustomerDashboardView.as_view(), name='customer'),
    path('vendor/', VendorDashboardView.as_view(), name='vendor'),
    path('admin/', AdminDashboardView.as_view(), name='admin'),
]