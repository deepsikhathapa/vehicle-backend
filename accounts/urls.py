from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    ProfileView,
    MyTokenObtainPairView,
    # AdminUserView
)
from .admin_views import AdminListView, AdminCostumerListView, AdminVendorListView, AdminUpdateView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),

    path('me/', ProfileView.as_view(), name='me'),
    # path('api/admin/users/', AdminUserView.as_view()),

    path('admin/users/', AdminListView.as_view(), name='admin_users'),
    path('admin/vendors/', AdminVendorListView.as_view(), name='admin_vendors'),
    path('admin/customers/', AdminCostumerListView.as_view(), name='admin_customer'),
    path('admin/users/<int:pk>/', AdminUpdateView.as_view()),
]
