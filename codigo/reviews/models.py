# ==========================================
# Autor: David Colás Martín
# ==========================================
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from rides.models import Ride

from .constants import DEFAULT_RATING, MAX_RATING, MIN_RATING


class Review(models.Model):
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=MIN_RATING)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.ride} by {self.user.username} - Rating: {self.rating}"

    def clean(self):
        """
        Valida los datos del modelo antes de guardarlo.
        """
        if self.rating < MIN_RATING or self.rating > MAX_RATING:
            raise ValidationError(
                f"Rating debe estar entre {MIN_RATING} y {MAX_RATING}."
            )

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para validar antes de guardar.
        """
        self.clean()
        super().save(*args, **kwargs)

    def is_valid_rating(self):
        """
        Verifica si el rating está dentro del rango válido.
        """
        return MIN_RATING <= self.rating <= MAX_RATING

    def get_stars_display(self):
        """
        Devuelve una representación de estrellas del rating.
        """
        return "⭐" * self.rating

    def get_ride_details(self):
        """
        Obtiene detalles formatados del viaje asociado.
        """
        if not self.ride:
            return "Sin viaje asociado"

        return f"{self.ride.origin} → {self.ride.destination}"
