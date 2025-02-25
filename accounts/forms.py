from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        label="Nombre de usuario",  # Etiqueta personalizada
        help_text="Ingrese un nombre de usuario único.",
        error_messages={
            'required': 'Este campo es obligatorio.',
            'unique': 'Este nombre de usuario ya está en uso.',
        }
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        label="Contraseña",  # Etiqueta personalizada
        help_text="Ingrese una contraseña segura.",
        error_messages={
            'required': 'Este campo es obligatorio.',
        }
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirmar contraseña",  # Etiqueta personalizada
        help_text="Ingrese la misma contraseña para verificación.",
        error_messages={
            'required': 'Este campo es obligatorio.',
        }
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')