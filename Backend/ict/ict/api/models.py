from django.db import models
from django.contrib.auth.models import AbstractUser

class Role(models.Model):
    """
    Model representing different user roles within the system.
    
    Attributes:
        name (str): The name of the role, ensuring uniqueness across records.
    """
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name 

class CustomUser(AbstractUser):
    """
    Extended user model that includes additional attributes for user customization and roles.
    
    Attributes:
        color (str): A hex color code representing the user profile.
        profile_access (ManyToManyField): Assignable roles for user permissions.
        phone_number (str): Optional phone number for the user.
        wilderness_track (ManyToManyField): Tracks associated with the user.
        gender (str): Gender of the user.
     
    Methods: 
        save: Overrides the default save method to automatically assign a default role ('Pending Approval') upon user creation.
    """
    color = models.TextField(null=False, blank=False, default='#000')
    profile_access = models.ManyToManyField(Role, blank=True, related_name='users')
    phone_number = models.TextField(null=True, blank=True, unique=True)
    gender = models.TextField(null=True, blank=True)
    email = models.EmailField(unique=True)
    # newFeatureViewed = models.BooleanField(blank=False, default=False)
    

class Instrument(models.Model):
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.symbol


class Candle(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name="candles")
    timestamp = models.DateTimeField()
    timeframe = models.CharField(max_length=10, default="5m")  # 1m, 5m, 15m, etc.
    _open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=["instrument", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.instrument.symbol} {self.timestamp} {self.timeframe}"
        