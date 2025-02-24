from django import forms
from .models import Ride

class RideForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = ['origin', 'destination', 'departure_time', 'total_seats', 'price']
        widgets = {
            'origin': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Madrid'
            }),
            'destination': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Barcelona'
            }),
            'departure_time': forms.DateTimeInput(attrs={
                'class': 'form-input',
                'type': 'datetime-local'
            }),
            'total_seats': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '1'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0'
            })
        }