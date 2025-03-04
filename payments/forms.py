from django import forms
from django.contrib.auth.models import User
from .models import Payment
from rides.models import Ride

#Formulario para crear un pago
class PaymentForm(forms.ModelForm):
    payment_method_choices = [
        ('credit_card', 'Tarjeta de crédito'),
        ('debit_card', 'Tarjeta de débito'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Transferencia bancaria'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=payment_method_choices,
        widget=forms.RadioSelect,
        label="Método de pago"
    )
    
    card_number = forms.CharField(
        required=False,
        max_length=19,
        widget=forms.TextInput(attrs={'placeholder': '1234 5678 9012 3456'}),
        label="Número de tarjeta"
    )
    
    expiry_date = forms.CharField(
        required=False,
        max_length=5,
        widget=forms.TextInput(attrs={'placeholder': 'MM/AA'}),
        label="Fecha de caducidad"
    )
    
    cvv = forms.CharField(
        required=False,
        max_length=4,
        widget=forms.TextInput(attrs={'placeholder': 'CVV'}),
        label="Código de seguridad (CVV)"
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        label="Acepto los términos y condiciones de pago"
    )
    
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method']
        widgets = {
            'amount': forms.NumberInput(attrs={'readonly': True}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].widget.attrs['readonly'] = True
        
        # Si se está editando un pago existente
        if 'instance' in kwargs and kwargs['instance']:
            # Deshabilitar campos según el estado del pago
            if kwargs['instance'].status != Payment.PENDING:
                for field in self.fields:
                    self.fields[field].widget.attrs['disabled'] = True
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        # Validaciones específicas según el método de pago
        if payment_method in ['credit_card', 'debit_card']:
            card_number = cleaned_data.get('card_number', '').replace(' ', '')
            expiry_date = cleaned_data.get('expiry_date')
            cvv = cleaned_data.get('cvv')
            
            if not card_number:
                self.add_error('card_number', 'El número de tarjeta es obligatorio')
            elif not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
                self.add_error('card_number', 'Número de tarjeta inválido')
            
            if not expiry_date:
                self.add_error('expiry_date', 'La fecha de caducidad es obligatoria')
            
            if not cvv:
                self.add_error('cvv', 'El código CVV es obligatorio')
            elif not cvv.isdigit() or len(cvv) < 3:
                self.add_error('cvv', 'Código CVV inválido')
        
        return cleaned_data

#Se usa para filtrar los pagos en la vista de lista de pagos
class PaymentFilterForm(forms.Form):
    STATUS_CHOICES = [
        ('', 'Todos los estados'),
        (Payment.PENDING, 'Pendiente'),
        (Payment.COMPLETED, 'Completado'),
        (Payment.FAILED, 'Fallido'),
        (Payment.REFUNDED, 'Reembolsado'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        label="Estado"
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Desde"
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Hasta"
    )
    
    min_amount = forms.DecimalField(
        required=False,
        decimal_places=2,
        label="Importe mínimo"
    )
    
    max_amount = forms.DecimalField(
        required=False,
        decimal_places=2,
        label="Importe máximo"
    )