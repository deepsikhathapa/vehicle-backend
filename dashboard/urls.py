from django.urls import path
from .views import CostumerDashboardView, VendorDashboardView, AdminDashboardView

urlpatterns = [
    path('costumer/', CostumerDashboardView.as_view(), name='costumer'),
    path('vendor/', VendorDashboardView.as_view(), name='vendor'),
    path('admin/', AdminDashboardView.as_view(), name='admin'),
]