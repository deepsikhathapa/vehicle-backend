from django.urls import path, include
from .views import CreateBookingView, MyBookingView, CancelBookingView, VendorBookingView, AdminBookingView


urlpatterns = [
    path('create/', CreateBookingView.as_view(), name='create'),
    path('my/', MyBookingView.as_view(), name='mybooking'),
    path('cancel/<int:pk>/', CancelBookingView.as_view(), name='cancel'),
    path('vendor/', VendorBookingView.as_view(), name='vendor'),
    path('admin/', AdminBookingView.as_view(), name='admin'),
]