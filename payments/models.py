from django.db import models
from django.contrib.auth.models import User
from rides.models import Ride
from django.conf import settings

# Create your models here.

class Payment(models.Model):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    
    STATUS_CHOICES = [
        (PENDING, 'Pendiente'),
        (COMPLETED, 'Completado'),
        (FAILED, 'Fallido'),
        (REFUNDED, 'Reembolsado'),
    ]
    
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='payments')
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_made')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_received')
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    payment_method = models.CharField(max_length=50)  # Tarjeta, PayPal, etc.
    transaction_id = models.CharField(max_length=100, blank=True, null=True)  # ID de transacción externo
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Pago de {self.payer.username} a {self.recipient.username}: {settings.CURRENCY_SYMBOL}{self.amount}"
