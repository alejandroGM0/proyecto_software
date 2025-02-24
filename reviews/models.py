from django.db import models
from django.contrib.auth.models import User
from rides.models import Ride

class Review(models.Model):
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=1)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.ride} by {self.user.username} - Rating: {self.rating}"
