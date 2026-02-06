from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Vehicle
from .serializers import VehicleSerializer, VehicleRecommendationSerializer, FareEstimationSerializer
from accounts.permissions import IsVendor, IsCustomer
from bookings.models import Booking
from rest_framework.exceptions import ValidationError
from activitylog.models import ActivityLog
from rest_framework.views import APIView
from rest_framework.response import Response
from decimal import Decimal


# Create your views here.


class VehicleListView(generics.ListAPIView):
    serializer_class = VehicleSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role == 'VENDOR':
            return Vehicle.objects.filter(owner=user)
        return Vehicle.objects.all()



class VendorVehicleListView(generics.ListAPIView):
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        return Vehicle.objects.filter(owner=self.request.user)



class VehicleCreateView(generics.CreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def perform_create(self, serializer):
        vehicle = serializer.save(owner=self.request.user)
        
        ActivityLog.objects.create(
            user = self.request.user,
            action = 'VEHICLE_ADD',
            description = f'Vehicle {serializer.instance.name} added.'
        )
        
    


class VehicleRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = VehicleSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsVendor()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role == 'VENDOR':
            # For safe methods, show all if they want to view details, 
            # but for updates/deletes they MUST be the owner.
            if self.request.method in ['PUT', 'PATCH', 'DELETE']:
                return Vehicle.objects.filter(owner=user)
        return Vehicle.objects.all()

    def perform_destroy(self, instance):
        active_bookings = Booking.objects.filter(
            vehicle=instance,
            status__in=['PENDING', 'CONFIRMED']
        ).exists()

        if active_bookings:
            raise ValidationError(
                "Cannot delete vehicle with active or confirmed bookings. Please cancel or complete bookings first."
            )
  
        ActivityLog.objects.create(
            user=self.request.user,
            action='VEHICLE_DELETE',
            description=f'Vehicle {instance.name} deleted.'
        )
        
        instance.delete()
    


class SmartVehicleRecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get_recommendations(self, data, user):
        serializer = VehicleRecommendationSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        passengers = serializer.validated_data['passengers']
        max_budget = serializer.validated_data['max_budget']
        trip_type = serializer.validated_data['trip_type']

        vehicles = Vehicle.objects.filter(
            capacity__gte=passengers,
            price_per_day__lte=max_budget,
            category=trip_type,
            is_available=True
        )

        if not vehicles.exists():
            vehicles = Vehicle.objects.filter(
                category=trip_type,
                capacity__gte=passengers,
                is_available=True
            ).order_by('price_per_day')[:3] 

        if user.is_authenticated and user.role == 'VENDOR':
            vehicles = vehicles.filter(owner=user)
        
        vehicles = vehicles.order_by('price_per_day')
        return vehicles

    def get(self, request):
        data = {
            'passengers': 4,
            'max_budget': 500,
            'trip_type': 'ECONOMY'
        }
        vehicles = self.get_recommendations(data, request.user)
        return Response(VehicleSerializer(vehicles, many=True).data)

    def post(self, request):
        vehicles = self.get_recommendations(request.data, request.user)
        return Response(VehicleSerializer(vehicles, many=True).data)
    


class FareEstimationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FareEstimationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        vehicle = Vehicle.objects.get(
            id=serializer.validated_data['vehicle_id']
        )

        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        distance = serializer.validated_data['distance_km']

        days = (end_date - start_date).days + 1

        base_price = vehicle.price_per_day * days

        distance_charge = distance * Decimal('5.00')  # ₹5 per km (example)

        multiplier = Decimal('1.0')
        if vehicle.category == 'LONG':
            multiplier = Decimal('1.2')
        elif vehicle.category == 'LUXURY':
            multiplier = Decimal('1.5')

        estimated_fare = (base_price + distance_charge) * multiplier

        return Response({
            "vehicle": vehicle.name,
            "days": days,
            "base_price": base_price,
            "distance_charge": distance_charge,
            "multiplier": multiplier,
            "estimated_fare": round(estimated_fare, 2)
        })
    


    
    
    
