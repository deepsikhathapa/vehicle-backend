from django.db import models
from accounts.models import User

# Create your models here.


class Vehicle(models.Model):
    CATEGORY_CHOICES = (
        ('ECONOMY', 'Economy'),
        ('LUXURY', 'Luxury'),
        ('FAMILY', 'Family'),
        ('BUSINESS', 'Business'),
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vehicles'
    )
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(default=4)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    images = models.ImageField(
        upload_to='vehicles/',
        null=True,
        blank=True
        )
    category = models.CharField(max_length=25, choices=CATEGORY_CHOICES, default='ECONOMY')
    is_available = models.BooleanField(default=True)
    base_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    per_km_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    per_hour_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)


    def __str__(self):
        return self.name
