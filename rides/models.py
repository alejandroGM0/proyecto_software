from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone

class Ride(models.Model):
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rides_as_driver')
    passengers = models.ManyToManyField(User, related_name='rides_as_passenger', blank=True)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    total_seats = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def get_formatted_price(self):
        return f"{settings.CURRENCY_SYMBOL}{self.price}"

    @property
    def seats_available(self):
        return self.total_seats - self.passengers.count()

    @property
    def is_active(self):
        return self.departure_time > timezone.now()

    def __str__(self):
        return f"{self.origin} → {self.destination} | {self.driver.username}"
