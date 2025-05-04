# ==========================================
# Autor: David Colás Martín
# ==========================================
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .constants import (PAYMENT_METHOD_CHOICES, PAYMENT_METHOD_CREDIT_CARD,
                        PAYMENT_STATUS_CHOICES, PAYMENT_STATUS_PENDING)


class Payment(models.Model):
    """
    Modelo para almacenar información de pagos
    """

    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments_made",
        verbose_name=_("Pagador"),
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments_received",
        verbose_name=_("Destinatario"),
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Importe")
    )
    ride = models.ForeignKey(
        "rides.Ride",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name=_("Viaje relacionado"),
    )
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_STATUS_PENDING,
        verbose_name=_("Estado"),
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default=PAYMENT_METHOD_CREDIT_CARD,
        verbose_name=_("Método de pago"),
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("ID de sesión de Stripe")
    )
    stripe_refund_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("ID de reembolso de Stripe"),
    )
    concept = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("Concepto")
    )
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notas"))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Fecha de creación")
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Fecha de actualización")
    )

    class Meta:
        verbose_name = _("Pago")
        verbose_name_plural = _("Pagos")
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.status:
            self.status = self.status.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pago #{self.id} - {self.amount}€ de {self.payer.username} a {self.recipient.username}"

    def get_absolute_url(self):
        return reverse("payments:payment_detail", kwargs={"pk": self.pk})

    def get_status_display(self):
        """
        Devuelve el texto de visualización para el estado del pago.
        Maneja casos donde el estado podría estar en minúsculas.
        """
        status_dict = dict(PAYMENT_STATUS_CHOICES)
        # Intentar buscar el estado directamente
        if self.status in status_dict:
            return status_dict[self.status]

        # Si no se encuentra, intentar con el estado en mayúsculas
        upper_status = self.status.upper() if self.status else ""
        if upper_status in status_dict:
            return status_dict[upper_status]

        # Si aún no se encuentra, devolver el estado sin procesar
        return self.status
