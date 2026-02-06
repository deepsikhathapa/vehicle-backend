from django.shortcuts import render
from rest_framework import generics, permissions
from accounts.permissions import IsAdmin
from .models import Booking
from .serializers import BookingSerializer
from activitylog.models import ActivityLog
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from notifications.models import Notification

# Create your views here.

class CreateBookingView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != 'COSTUMER':
            raise PermissionDenied('Only customers can create bookings.')

        # vehicle = get_object_or_404(Vehicle, id=self.request.data.get('vehicle'))
        vehicle = serializer.validated_data['vehicle']

        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']

        # conflict = Booking.objects.filter(
        #     vehicle=vehicle,
        #     status='CONFIRMED',
        #     start_date__lte=end_date,
        #     end_date__gte=start_date
        # ).exists()

        # if conflict:
        #     raise ValidationError("Vehicle is already booked for selected dates")

        days = (end_date - start_date).days + 1
        total_price = days * vehicle.price_per_day

        booking = serializer.save(
            costumer=user,
            vehicle=vehicle,
            total_price=total_price,
            status='CONFIRMED'
        )

        ActivityLog.objects.create(
            user=user,
            action='BOOKING_CREATE',
            description=f'Booking ID {booking.id} created'
        )

        # Notify Customer
        Notification.objects.create(
            recipient=user,
            title="Booking Confirmed",
            message=f"Your booking for {vehicle.name} from {start_date} to {end_date} has been confirmed!",
            notification_type='SUCCESS'
        )

        # Notify Vendor
        if vehicle.owner:
            Notification.objects.create(
                recipient=vehicle.owner,
                title="New Booking Received",
                message=f"New booking for {vehicle.name} by {user.username} from {start_date} to {end_date}.",
                notification_type='INFO'
            )



class MyBookingView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(costumer=self.request.user).select_related('vehicle', 'vehicle__owner')
    

class CancelBookingView(generics.UpdateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Booking.objects.all()
        if user.role == 'VENDOR':
            return Booking.objects.filter(vehicle__owner=user)
        # Default: fall back to COSTUMER (their own bookings)
        return Booking.objects.filter(costumer=user)

    def perform_update(self, serializer):
        booking = serializer.save(status='CANCELLED')
        

        ActivityLog.objects.create(
            user=self.request.user,
            action='BOOKING_CANCEL',
            description=f'Booking ID {booking.id} cancelled'
        )

        # Notify the other party about cancellation
        if self.request.user == booking.costumer:
            # Customer cancelled -> Notify Vendor
            if booking.vehicle.owner:
                Notification.objects.create(
                    recipient=booking.vehicle.owner,
                    title="Booking Cancelled",
                    message=f"Booking #{booking.id} for {booking.vehicle.name} was cancelled by the customer.",
                    notification_type='WARNING'
                )
        elif self.request.user == booking.vehicle.owner:
            # Vendor cancelled -> Notify Customer
            Notification.objects.create(
                recipient=booking.costumer,
                title="Booking Cancelled by Vendor",
                message=f"Your booking #{booking.id} for {booking.vehicle.name} was cancelled by the vendor.",
                notification_type='ERROR'
            )
    

class VendorBookingView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_queryset(self):
        user = self.request.user
        if user.role != 'VENDOR':
            return Booking.objects.none()
        
        return Booking.objects.filter(vehicle__owner=user)
    

class AdminBookingView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return Booking.objects.all()



    
