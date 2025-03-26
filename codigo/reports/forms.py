from django import forms
from .models import Report
from .constants import (
    PAYMENT_TYPE, RIDE_TYPE, USER_TYPE, SYSTEM_TYPE,
    NORMAL_IMPORTANCE, IMPORTANT_IMPORTANCE, URGENT_IMPORTANCE
)

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['title', 'description', 'report_type', 'importance']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ReportResponseForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['response']
        widgets = {
            'response': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escribe tu respuesta...'}),
        }

class ReportFilterForm(forms.Form):
    TYPE_CHOICES = [
        ('', 'Todos los tipos'),
    ] + Report.TYPE_CHOICES
    
    IMPORTANCE_CHOICES = [
        ('', 'Todas las importancias'),
    ] + Report.IMPORTANCE_CHOICES
    
    report_type = forms.ChoiceField(choices=TYPE_CHOICES, required=False)
    importance = forms.ChoiceField(choices=IMPORTANCE_CHOICES, required=False)
    read = forms.BooleanField(required=False, label="Solo mostrar no leídos")
    search = forms.CharField(required=False, label="Buscar")