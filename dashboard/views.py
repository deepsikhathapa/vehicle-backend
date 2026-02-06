from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models


from accounts.permissions import IsAdmin, IsVendor, IsCustomer
from accounts.models import User
from vehicles.models import Vehicle
from bookings.models import Booking
from .serializers import VendorDashboardSerializer, AdminDashboardSerializer, CostumerDashboardSerializer

# Create your views here.

class CostumerDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def get(self, request):
        customer = request.user

        bookings = Booking.objects.filter(costumer=customer)

        data = {
            "total_bookings": bookings.count(),
            "active_bookings": bookings.filter(status='CONFIRMED').count(),
            "cancelled_bookings": bookings.filter(status='CANCELLED').count(),
            "completed_bookings": bookings.filter(status='COMPLETED').count(),
            "total_spent": bookings.filter(
                status='CONFIRMED'
            ).aggregate(total=models.Sum('total_price'))['total'] or 0,
        }

        serializer = CostumerDashboardSerializer(data)
        return Response(serializer.data)
    


class VendorDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsVendor]

    def get(self, request):
        vendor = request.user

        vehicles = Vehicle.objects.filter(owner=vendor)
        bookings = Booking.objects.filter(vehicle__owner=vendor)

        data = {
            "total_vehicles": vehicles.count(),
            "total_bookings": bookings.count(),
            "active_bookings": bookings.filter(status='CONFIRMED').count(),
            "cancelled_bookings": bookings.filter(status='CANCELLED').count(),
            "total_earnings": bookings.filter(
                status='CONFIRMED'
            ).aggregate(total=models.Sum('total_price'))['total'] or 0,
        }

        serializer = VendorDashboardSerializer(data)
        return Response(serializer.data)




class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        data = {
            "total_users": User.objects.count(),
            "total_customers": User.objects.filter(role='COSTUMER').count(),
            "total_vendors": User.objects.filter(role='VENDOR').count(),
            "total_bookings": Booking.objects.count(),
            "total_vehicles": Vehicle.objects.count(),
        }

        serializer = AdminDashboardSerializer(data)
        return Response(serializer.data)


