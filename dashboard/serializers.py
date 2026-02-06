from rest_framework import serializers

class AdminDashboardSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    total_vendors = serializers.IntegerField()
    total_bookings = serializers.IntegerField()
    total_vehicles = serializers.IntegerField()



class VendorDashboardSerializer(serializers.Serializer):
    total_vehicles = serializers.IntegerField()
    total_bookings = serializers.IntegerField()
    active_bookings = serializers.IntegerField()
    cancelled_bookings = serializers.IntegerField()
    total_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)



class CostumerDashboardSerializer(serializers.Serializer):
    total_bookings = serializers.IntegerField()
    active_bookings = serializers.IntegerField()
    cancelled_bookings = serializers.IntegerField()
    completed_bookings = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2)

