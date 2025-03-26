from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Foto de perfil
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True, verbose_name="Foto de perfil")
    
    # Información personal
    bio = models.TextField(blank=True, null=True, verbose_name="Biografía")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Número de teléfono")
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ciudad de residencia")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Fecha de nacimiento")
    
    # Detalles del vehículo
    has_vehicle = models.BooleanField(default=False, verbose_name="¿Tienes vehículo?")
    vehicle_model = models.CharField(max_length=100, blank=True, null=True, verbose_name="Modelo del vehículo")
    vehicle_year = models.PositiveIntegerField(null=True, blank=True, verbose_name="Año del vehículo")
    vehicle_color = models.CharField(max_length=50, blank=True, null=True, verbose_name="Color del vehículo")
    vehicle_features = models.TextField(blank=True, null=True, verbose_name="Características adicionales")
    
    # Preferencias de viaje
    MUSIC_CHOICES = [
        ('any', 'Cualquiera'),
        ('pop', 'Pop'),
        ('rock', 'Rock'),
        ('electronic', 'Electrónica'),
        ('classical', 'Clásica'),
        ('none', 'Prefiero silencio'),
    ]
    
    TALK_CHOICES = [
        ('chatty', 'Me gusta conversar'),
        ('quiet', 'Prefiero silencio'),
        ('depends', 'Depende del momento'),
    ]
    
    pref_music = models.CharField(max_length=20, choices=MUSIC_CHOICES, default='any', verbose_name="Música")
    pref_talk = models.CharField(max_length=20, choices=TALK_CHOICES, default='depends', verbose_name="Conversación")
    pref_pets = models.BooleanField(default=False, verbose_name="Acepto mascotas")
    pref_smoking = models.BooleanField(default=False, verbose_name="Permito fumar")
    
    # Preferencias de notificaciones
    email_notifications = models.BooleanField(default=True)
    message_notifications = models.BooleanField(default=True)
    ride_notifications = models.BooleanField(default=True)
    
    # Preferencias de privacidad
    profile_visible = models.BooleanField(default=True)
    show_rides_history = models.BooleanField(default=True)
    
    # Actividad en la plataforma
    last_active = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    def get_age(self):
        if self.birth_date:
            today = timezone.now().date()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None
    
    def get_activity_status(self):
        now = timezone.now()
        diff = now - self.last_active
        
        if diff.days == 0:
            if diff.seconds < 3600:
                return "En línea recientemente"
            return "Hoy"
        elif diff.days == 1:
            return "Ayer"
        elif diff.days < 7:
            return f"Hace {diff.days} días"
        elif diff.days < 30:
            return f"Hace {diff.days // 7} semanas"
        else:
            return f"Hace {diff.days // 30} meses"
