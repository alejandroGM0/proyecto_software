# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.tests.test_constants import *


class AuthenticationTests(TestCase):
    """Pruebas para la autenticación de usuarios"""

    def setUp(self):
        """Configura un usuario de prueba y un cliente para las solicitudes HTTP"""
        self.user = User.objects.create_user(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD
        )
        self.client = Client()

    def test_login_logout(self):
        """Verifica el proceso de inicio y cierre de sesión"""
        response = self.client.get(reverse(URL_PROFILE))
        self.assertEqual(response.status_code, 302)

        login_successful = self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        self.assertTrue(login_successful)

        response = self.client.get(reverse(URL_SETTINGS))
        self.assertEqual(response.status_code, 200)

        self.client.logout()

        response = self.client.get(reverse(URL_SETTINGS))
        self.assertEqual(response.status_code, 302)

    def test_login_invalid_credentials(self):
        """Verifica que no se pueda iniciar sesión con credenciales inválidas"""
        login_successful = self.client.login(username=TEST_USERNAME, password=WRONG_PASSWORD)
        self.assertFalse(login_successful)

        login_successful = self.client.login(username=NEW_USER, password=TEST_PASSWORD)
        self.assertFalse(login_successful)


class PasswordChangeTests(TestCase):
    """Pruebas para el cambio de contraseña"""

    def setUp(self):
        """Configura un usuario de prueba y un cliente con sesión iniciada"""
        self.user = User.objects.create_user(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=COMPLEX_PASSWORD
        )
        self.client = Client()
        self.client.login(username=TEST_USERNAME, password=COMPLEX_PASSWORD)

    def test_change_password_view(self):
        """Verifica que la vista de cambio de contraseña se carga correctamente"""
        response = self.client.get(reverse(URL_CHANGE_PASSWORD))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_CHANGE_PASSWORD)

    def test_change_password_success(self):
        """Verifica que se pueda cambiar la contraseña correctamente"""
        response = self.client.post(reverse(URL_CHANGE_PASSWORD), {
            FIELD_OLD_PASSWORD: COMPLEX_PASSWORD,
            FIELD_NEW_PASSWORD1: NEW_PASSWORD,
            FIELD_NEW_PASSWORD2: NEW_PASSWORD
        })

        self.assertEqual(response.status_code, 302)

        self.client.logout()
        success = self.client.login(username=TEST_USERNAME, password=NEW_PASSWORD)
        self.assertTrue(success)

    def test_change_password_incorrect_old(self):
        """Verifica que no se pueda cambiar la contraseña si la antigua es incorrecta"""
        response = self.client.post(reverse(URL_CHANGE_PASSWORD), {
            FIELD_OLD_PASSWORD: WRONG_PASSWORD,
            FIELD_NEW_PASSWORD1: NEW_PASSWORD,
            FIELD_NEW_PASSWORD2: NEW_PASSWORD
        })

        self.assertEqual(response.status_code, 200)

        self.client.logout()
        success = self.client.login(username=TEST_USERNAME, password=COMPLEX_PASSWORD)
        self.assertTrue(success)

    def test_change_password_mismatch(self):
        """Verifica que no se pueda cambiar la contraseña si las nuevas no coinciden"""
        response = self.client.post(reverse(URL_CHANGE_PASSWORD), {
            FIELD_OLD_PASSWORD: COMPLEX_PASSWORD,
            FIELD_NEW_PASSWORD1: NEW_PASSWORD,
            FIELD_NEW_PASSWORD2: DIFFERENT_PASSWORD_LONG
        })

        self.assertEqual(response.status_code, 200)

        self.client.logout()
        success = self.client.login(username=TEST_USERNAME, password=COMPLEX_PASSWORD)
        self.assertTrue(success)