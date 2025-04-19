from django.test import TestCase
from django.contrib.auth.models import User
from payments.tests.test_constants import *
from payments.forms import PaymentInitForm

class PaymentFormsTests(TestCase):
    """
    Pruebas para los formularios de pagos.
    """
    
    def test_payment_init_form_valid(self):
        """
        Prueba que el formulario acepta datos válidos.
        """
        print("\nProbando formulario con datos válidos...")
        
        form_data = {
            'terms_accepted': True
        }
        form = PaymentInitForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_payment_init_form_invalid(self):
        """
        Prueba que el formulario rechaza datos inválidos.
        """
        print("\nProbando formulario con datos inválidos...")
        
        # Sin aceptar términos
        form_data = {}
        form = PaymentInitForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('terms_accepted', form.errors)
        
        # Términos explícitamente falsos
        form_data = {'terms_accepted': False}
        form = PaymentInitForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('terms_accepted', form.errors)
