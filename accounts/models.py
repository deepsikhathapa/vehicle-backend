from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):

    ROLE_CHOICES = (
        ('VENDOR', 'Vendor'),
        ('COSTUMER', 'Costumer'),
        ('ADMIN', 'Admin'),
    )


    role = models.CharField(max_length=25, choices=ROLE_CHOICES, default='COSTUMER')

    def __str__(self):
        return  f'{self.username}'






