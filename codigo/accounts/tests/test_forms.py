from django.test import TestCase
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from accounts.tests.test_constants import *


class UserCreationFormTest(TestCase):
    """Pruebas para el formulario de registro de usuario"""

    def test_form_has_expected_fields(self):
        """Verifica que el formulario tiene los campos esperados"""
        form = UserCreationForm()
        expected_fields = [USERNAME_FIELD, PASSWORD1_FIELD, PASSWORD2_FIELD]

        for field in expected_fields:
            self.assertIn(field, form.fields)

    def test_password_validation(self):
        """Prueba la validación de contraseñas que coinciden y que no coinciden"""
        form_data = {
            USERNAME_FIELD: NEW_USER,
            PASSWORD1_FIELD: COMPLEX_PASSWORD,
            PASSWORD2_FIELD: COMPLEX_PASSWORD
        }
        form = UserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

        form_data = {
            USERNAME_FIELD: NEW_USER,
            PASSWORD1_FIELD: COMPLEX_PASSWORD,
            PASSWORD2_FIELD: DIFFERENT_PASSWORD
        }
        form = UserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(PASSWORD2_FIELD, form.errors)

    def test_username_uniqueness(self):
        """Prueba que el nombre de usuario debe ser único"""
        User.objects.create_user(username=EXISTING_USERNAME, password=TEST_PASSWORD)

        form_data = {
            USERNAME_FIELD: EXISTING_USERNAME,
            PASSWORD1_FIELD: COMPLEX_PASSWORD,
            PASSWORD2_FIELD: COMPLEX_PASSWORD
        }
        form = UserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(USERNAME_FIELD, form.errors)


class AuthenticationFormTest(TestCase):
    """Pruebas para el formulario de autenticación"""

    def setUp(self):
        """Configura un usuario para las pruebas de autenticación"""
        self.user = User.objects.create_user(
            username=TEST_USERNAME,
            password=TEST_PASSWORD
        )

    def test_form_authentication_valid(self):
        """Prueba la autenticación con credenciales válidas"""
        form_data = {
            USERNAME_FIELD: TEST_USERNAME,
            PASSWORD_FIELD: TEST_PASSWORD
        }
        form = AuthenticationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_authentication_invalid(self):
        """Prueba la autenticación con credenciales inválidas"""
        form_data = {
            USERNAME_FIELD: TEST_USERNAME,
            PASSWORD_FIELD: WRONG_PASSWORD
        }
        form = AuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())
