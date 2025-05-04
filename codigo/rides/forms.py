# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
from django import forms
from .models import Ride
from .constants import ORIGIN_KEY, DESTINATION_KEY, DATE_KEY

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
        
class RideSearchForm(forms.Form):
    origin = forms.CharField(
        label='Origen',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ciudad de origen'})
    )
    destination = forms.CharField(
        label='Destino',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ciudad de destino'})
    )
    date = forms.DateField(
        label='Fecha',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    time_from = forms.TimeField(
        label='Desde las',
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time'})
    )
    time_to = forms.TimeField(
        label='Hasta las',
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time'})
    )
    price_min = forms.DecimalField(
        label='Precio mínimo',
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Min', 'step': '0.01'})
    )
    price_max = forms.DecimalField(
        label='Precio máximo',
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Max', 'step': '0.01'})
    )
    allows_smoking = forms.BooleanField(
        label='Permite fumar',
        required=False,
        widget=forms.CheckboxInput()
    )
    allows_pets = forms.BooleanField(
        label='Permite mascotas',
        required=False,
        widget=forms.CheckboxInput()
    )

    class Meta:
        fields = [ORIGIN_KEY, DESTINATION_KEY, DATE_KEY, 'time_from', 'time_to', 
                 'price_min', 'price_max', 'allows_smoking', 'allows_pets']