from django.db import models
from accounts.models import User

# Create your models here.

class ActivityLog(models.Model):

    ACTION_CHOICES = (
        ('REGISTER', 'Register'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('VEHICLE_ADD', 'Vehicle Added'),
        ('BOOKING_CREATE', 'Booking Created'),
        ('BOOKING_CANCEL', 'Booking Cancelled'),
        ('ROLE_CHANGE', 'Role Changed'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.action}'
