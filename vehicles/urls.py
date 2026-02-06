from django.urls import path
from .views import (VehicleListView, VehicleCreateView, VehicleRetrieveUpdateDeleteView, 
 SmartVehicleRecommendationView, FareEstimationView, VendorVehicleListView)

urlpatterns = [
    path('', VehicleListView.as_view(), name='vehicle_list'),
    path('vendor-vehicles/', VendorVehicleListView.as_view(), name='vendor_vehicle_list'),
    path('add/', VehicleCreateView.as_view(), name='vehicle_add'),
    path('<int:pk>/', VehicleRetrieveUpdateDeleteView.as_view(), name='vehicle_details'),
    path(
        'recommend/',
        SmartVehicleRecommendationView.as_view(),
        name='vehicle-recommendation'
    ),
      path(
        'fare-estimate/',
        FareEstimationView.as_view(),
        name='fare-estimation'
    ),
]