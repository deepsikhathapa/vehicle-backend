from rest_framework import serializers
from .models import Booking
from vehicles.models import Vehicle
from datetime import date

class BookingSerializer(serializers.ModelSerializer):
    costumer = serializers.ReadOnlyField(source='costumer.username')
    vehicle_name = serializers.ReadOnlyField(source='vehicle.name')
    vendor_name = serializers.ReadOnlyField(source='vehicle.owner.username')


    class Meta:
        model = Booking
        fields = [
            'id',
            'costumer',
            'vehicle', 
            'vehicle_name',
            'vendor_name',
            'start_date',
            'end_date',
            'total_price',
            'status',
            'created_at',
            'pickup_location',
            'pickup_time',
            'dropoff_location',
            'dropoff_time',
        ]
        read_only_fields = ['total_price', 'created_at']

    
    def validate(self, data):
       
        instance = self.instance
        vehicle = data.get('vehicle', getattr(instance, 'vehicle', None))
        start = data.get('start_date', getattr(instance, 'start_date', None))
        end = data.get('end_date', getattr(instance, 'end_date', None))
        status = data.get('status', getattr(instance, 'status', 'PENDING'))

        if not vehicle or not start or not end:
            return data

        
        if instance and instance.start_date == start:
            pass
        elif start < date.today():
            raise serializers.ValidationError('Start date cannot be in the past.')
        
        if end < start:
            raise serializers.ValidationError("End date must be after start date.")
        
        
        if status == 'CONFIRMED' or instance is None:
            queryset = Booking.objects.filter(
                vehicle=vehicle,
                status='CONFIRMED',
                start_date__lte=end,
                end_date__gte=start
            )
            
            
            if instance:
                queryset = queryset.exclude(id=instance.id)

            if queryset.exists():
                raise serializers.ValidationError(
                    "This vehicle is already booked for the selected dates."
                )

        return data
    

    

