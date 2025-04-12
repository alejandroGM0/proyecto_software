# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        label="Nombre de usuario",  
        help_text="Ingrese un nombre de usuario único.",
        error_messages={
            'required': 'Este campo es obligatorio.',
            'unique': 'Este nombre de usuario ya está en uso.',
        }
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        label="Contraseña",  
        help_text="Ingrese una contraseña segura.",
        error_messages={
            'required': 'Este campo es obligatorio.',
        }
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirmar contraseña",  
        help_text="Ingrese la misma contraseña para verificación.",
        error_messages={
            'required': 'Este campo es obligatorio.',
        }
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'profile_image', 'bio', 'phone_number', 'location', 'birth_date',
            'has_vehicle', 'vehicle_model', 'vehicle_year', 'vehicle_color', 'vehicle_features',
            'pref_music', 'pref_talk', 'pref_pets', 'pref_smoking',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Cuéntanos un poco sobre ti...'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'vehicle_features': forms.Textarea(attrs={'rows': 3, 'placeholder': 'A/C, maletero amplio, etc.'}),
        }

