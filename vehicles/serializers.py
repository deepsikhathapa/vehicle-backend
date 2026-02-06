from rest_framework import serializers
from .models import Vehicle
from datetime import date


class VehicleSerializer(serializers.ModelSerializer):

    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Vehicle
        fields = [
            'id',
            'owner',
            'name',
            'price_per_day',
            'is_available',
            'category',
            'capacity',
            'images',
            'base_price',
            'per_km_rate',
            'per_hour_rate',
        ]


class VehicleRecommendationSerializer(serializers.Serializer):
    passengers = serializers.IntegerField(min_value=1)
    max_budget = serializers.DecimalField(max_digits=10, decimal_places=2)
    trip_type = serializers.ChoiceField(
        choices=[
            ('ECONOMY', 'Economy'),
            ('LUXURY', 'Luxury'),
            ('FAMILY', 'Family'),
            ('BUSINESS', 'Business'),
        ]
    )


class FareEstimationSerializer(serializers.Serializer):
    vehicle_id = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    distance_km = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0, required=False, default=0)

    def validate(self, data):
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError(
                "End date must be after start date"
            )
        return data