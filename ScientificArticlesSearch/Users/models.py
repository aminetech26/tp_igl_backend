from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('User', 'User'),
        ('Mod', 'Moderator'),
        ('Admin', 'Admin'),
    ]
    #an AbstractUser django class have already the fields that we need
    #we just need to add the user-type attribute
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='User',)
    #username is already included in REQUIRED_FIELDS so i removed it
    REQUIRED_FIELDS = ['password','user_type']
    def __str__(self):
        return f"{self.username} ({self.user_type})"