from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.

class User(AbstractUser):

    CUSTOMER = 'customer'
    VENDOR = 'vendor'

    ROLE_CHOICES = (
        ('VENDOR', 'Vendor'),
        ('CUSTOMER', 'Customer'),
        ('ADMIN', 'Admin'),
    )


    role = models.CharField(max_length=25, choices=ROLE_CHOICES, default='CUSTOMER')
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return  f'{self.username}'






