from django import forms
from django.utils.translation import gettext_lazy as _

class PaymentInitForm(forms.Form):
    """
    Formulario para iniciar un pago mediante redirección a Stripe
    """
    terms_accepted = forms.BooleanField(
        required=True,
        label=_("Acepto los términos y condiciones de pago"),
        error_messages={
            'required': _("Debes aceptar los términos y condiciones para continuar.")
        }
    )

class PaymentForm(forms.Form):
    """
    Formulario para procesar un pago con Stripe
    """
    terms_accepted = forms.BooleanField(
        required=True,
        label=_("Acepto los términos y condiciones de pago y confirmo que quiero reservar este viaje."),
        error_messages={
            'required': _("Debes aceptar los términos y condiciones para continuar.")
        }
    )
