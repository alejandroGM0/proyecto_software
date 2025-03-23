from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class Report(models.Model):
    # Tipos de reporte
    PAYMENT = 'payment'
    RIDE = 'ride'
    USER = 'user'
    SYSTEM = 'system'
    
    TYPE_CHOICES = [
        (PAYMENT, 'Pago'),
        (RIDE, 'Viaje'),
        (USER, 'Usuario'),
        (SYSTEM, 'Sistema'),
    ]
    
    # Niveles de importancia
    NORMAL = 'normal'
    IMPORTANT = 'important'
    URGENT = 'urgent'
    
    IMPORTANCE_CHOICES = [
        (NORMAL, 'Normal'),
        (IMPORTANT, 'Importante'),
        (URGENT, 'Urgente'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")
    report_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=SYSTEM, verbose_name="Tipo")
    importance = models.CharField(max_length=10, choices=IMPORTANCE_CHOICES, default=NORMAL, verbose_name="Importancia")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports', verbose_name="Usuario")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    read = models.BooleanField(default=False, verbose_name="Leído")
    
    response = models.TextField(blank=True, null=True, verbose_name="Respuesta")
    response_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='responses', verbose_name="Respondido por")
    response_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de respuesta")
    
    def get_absolute_url(self):
        return reverse('reports:report_detail', kwargs={'pk': self.pk})
    
    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
