# ==========================================
# Autor: David Colás Martín
# ==========================================
from django import forms

from .constants import (IMPORTANT_IMPORTANCE, NORMAL_IMPORTANCE, PAYMENT_TYPE,
                        RIDE_TYPE, SYSTEM_TYPE, URGENT_IMPORTANCE, USER_TYPE)
from .models import Report


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["title", "description", "report_type", "importance"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class ReportResponseForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["response"]
        widgets = {
            "response": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Escribe tu respuesta..."}
            ),
        }


class ReportFilterForm(forms.Form):
    TYPE_CHOICES = [
        ("", "Todos los tipos"),
    ] + Report.TYPE_CHOICES

    IMPORTANCE_CHOICES = [
        ("", "Todas las importancias"),
    ] + Report.IMPORTANCE_CHOICES

    STATUS_CHOICES = [
        ("", "Todos los estados"),
        ("unread", "No leídos"),
        ("read", "Leídos"),
        ("responded", "Respondidos"),
    ]

    report_type = forms.ChoiceField(choices=TYPE_CHOICES, required=False)
    importance = forms.ChoiceField(choices=IMPORTANCE_CHOICES, required=False)
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    search = forms.CharField(required=False, label="Buscar")
