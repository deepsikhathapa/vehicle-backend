from django.db import models
from accounts.models import User
from vehicles.models import Vehicle

# Create your models here.

class Booking(models.Model):

    STATUS_CHOICE=(
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    )

    costumer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings'
        )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICE,
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    pickup_location = models.CharField(max_length=255, null=True, blank=True)
    pickup_time = models.TimeField(null=True, blank=True)
    dropoff_location = models.CharField(max_length=255, null=True, blank=True)
    dropoff_time = models.TimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.costumer.username} -> {self.vehicle.name}'
    



