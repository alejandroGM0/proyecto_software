# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from accounts.models import UserProfile
from accounts.tests.test_constants import *


class LoginViewTests(TestCase):
    """Pruebas para la vista de login"""

    def setUp(self):
        """Configura los datos de prueba para los tests de login"""
        self.user = User.objects.create_user(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD
        )
        self.client = Client()

    def test_login_view_get(self):
        """Verifica que la página de login se carga correctamente"""
        response = self.client.get(reverse(URL_LOGIN))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_LOGIN)

    def test_login_view_post_valid(self):
        """Verifica que se puede iniciar sesión con credenciales válidas"""
        response = self.client.post(reverse(URL_LOGIN), {
            FIELD_USERNAME: TEST_USERNAME,
            FIELD_PASSWORD: TEST_PASSWORD
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_view_post_invalid(self):
        """Verifica que no se puede iniciar sesión con credenciales inválidas"""
        response = self.client.post(reverse(URL_LOGIN), {
            FIELD_USERNAME: TEST_USERNAME,
            FIELD_PASSWORD: INVALID_PASSWORD
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class RegisterViewTests(TestCase):
    """Pruebas para la vista de registro"""

    def setUp(self):
        """Configura el cliente para las pruebas de registro"""
        self.client = Client()

    def test_register_view_get(self):
        """Verifica que la página de registro se carga correctamente"""
        response = self.client.get(reverse(URL_REGISTER))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_REGISTER)

    def test_register_view_post_valid(self):
        """Verifica que se puede registrar un usuario con datos válidos"""
        response = self.client.post(reverse(URL_REGISTER), {
            FIELD_USERNAME: NEW_USER,
            FIELD_EMAIL: NEW_EMAIL,
            FIELD_PASSWORD1: NEW_PASSWORD,
            FIELD_PASSWORD2: NEW_PASSWORD,
            FIELD_LOCATION: TEST_LOCATION_MADRID,
            FIELD_BIO: TEST_BIO,
            FIELD_PHONE: TEST_PHONE,
            FIELD_PREF_MUSIC: TEST_MUSIC_ROCK,
            FIELD_PREF_TALK: TEST_TALK_CHATTY,
        })

        if response.status_code == 200:
            print(f"Form errors: {response.context[CONTEXT_USER_FORM].errors}")
            print(f"Profile form errors: {response.context[CONTEXT_PROFILE_FORM].errors}")

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username=NEW_USER).exists())
        self.assertTrue(UserProfile.objects.filter(user__username=NEW_USER).exists())

    def test_register_view_post_invalid(self):
        """Verifica que no se puede registrar un usuario con contraseñas diferentes"""
        response = self.client.post(reverse(URL_REGISTER), {
            FIELD_USERNAME: NEW_USER,
            FIELD_EMAIL: NEW_EMAIL,
            FIELD_PASSWORD1: NEW_PASSWORD,
            FIELD_PASSWORD2: DIFFERENT_PASSWORD
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=NEW_USER).exists())


class ProfileViewTests(TestCase):
    """Pruebas para la vista de perfil de usuario"""

    def setUp(self):
        """Configura usuario, perfil y cliente para las pruebas de perfil"""
        self.user = User.objects.create_user(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD
        )

        self.profile = UserProfile.objects.create(
            user=self.user,
            bio="Biografía de prueba",
            location=TEST_LOCATION_BARCELONA
        )

        self.client = Client()

    def test_profile_view(self):
        """Verifica que se puede ver el perfil de un usuario"""
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

        response = self.client.get(reverse(URL_PROFILE_VIEW, kwargs={FIELD_USERNAME: TEST_USERNAME}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_PROFILE)
        self.assertEqual(response.context[CONTEXT_USER_PROFILE].user, self.user)

    def test_profile_redirect(self):
        """Verifica que la URL de perfil redirige al perfil del usuario actual"""
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

        response = self.client.get(reverse(URL_PROFILE))
        self.assertEqual(response.status_code, 302)
        self.assertIn(TEST_USERNAME, response.url)


class SettingsViewTests(TestCase):
    """Pruebas para la vista de configuración de perfil"""

    def setUp(self):
        """Configura usuario, perfil y cliente para las pruebas de configuración"""
        self.user = User.objects.create_user(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD
        )

        self.profile = UserProfile.objects.create(
            user=self.user,
            bio="Biografía de prueba"
        )

        self.client = Client()

    def test_settings_view_requires_authentication(self):
        """Verifica que se requiere autenticación para acceder a la configuración"""
        response = self.client.get(reverse(URL_SETTINGS))

        self.assertEqual(response.status_code, 302)
        self.assertIn(LOGIN_URL_PART, response.url)

        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        response = self.client.get(reverse(URL_SETTINGS))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_SETTINGS)

    def test_settings_update(self):
        """Verifica que se pueden actualizar todas las configuraciones del perfil"""
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

        new_data = {
            FIELD_SETTINGS_TYPE: SETTINGS_TYPE_PROFILE,
            FIELD_BIO: NEW_BIO,
            FIELD_LOCATION: TEST_LOCATION_VALENCIA,
            FIELD_PHONE: TEST_NEW_PHONE,
            FIELD_HAS_VEHICLE: ON_VALUE,
            FIELD_VEHICLE_MODEL: VEHICLE_MODEL, 
            FIELD_VEHICLE_YEAR: VEHICLE_YEAR,
            FIELD_VEHICLE_COLOR: VEHICLE_COLOR,
            FIELD_PREF_MUSIC: TEST_MUSIC_POP,
            FIELD_PREF_TALK: TEST_TALK_QUIET,
            FIELD_PREF_PETS: ON_VALUE,
            FIELD_PREF_SMOKING: ON_VALUE,
            FIELD_EMAIL_NOTIFICATIONS: ON_VALUE
        }

        response = self.client.post(reverse(URL_SETTINGS), new_data)

        self.assertEqual(response.status_code, 200)
        
        messages = list(response.context[CONTEXT_MESSAGES])
        self.assertTrue(any(MSG_PROFILE_UPDATED in str(msg) for msg in messages))
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, NEW_BIO)
        self.assertEqual(self.profile.location, TEST_LOCATION_VALENCIA)

    def test_profile_settings_update(self):
        """Verifica que se pueden actualizar solo los datos básicos del perfil"""
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        
        profile_data = {
            FIELD_SETTINGS_TYPE: SETTINGS_TYPE_PROFILE,
            FIELD_BIO: NEW_BIO,
            FIELD_LOCATION: TEST_LOCATION_VALENCIA,
            FIELD_PHONE: TEST_NEW_PHONE
        }
        
        response = self.client.post(reverse(URL_SETTINGS), profile_data)
        self.assertEqual(response.status_code, 200)
        
        messages = list(response.context[CONTEXT_MESSAGES])
        self.assertTrue(any(MSG_PROFILE_UPDATED in str(msg) for msg in messages))
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, NEW_BIO)
        self.assertEqual(self.profile.location, TEST_LOCATION_VALENCIA)

    def test_vehicle_settings_update(self):
        """Verifica que se pueden actualizar los datos del vehículo"""
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        
        vehicle_data = {
            FIELD_SETTINGS_TYPE: SETTINGS_TYPE_VEHICLE,
            FIELD_HAS_VEHICLE: ON_VALUE,
            FIELD_VEHICLE_MODEL: VEHICLE_MODEL,
            FIELD_VEHICLE_YEAR: VEHICLE_YEAR,
            FIELD_VEHICLE_COLOR: VEHICLE_COLOR
        }
        
        response = self.client.post(reverse(URL_SETTINGS), vehicle_data)
        self.assertEqual(response.status_code, 200)
        
        messages = list(response.context[CONTEXT_MESSAGES])
        self.assertTrue(any(MSG_VEHICLE_UPDATED in str(msg) for msg in messages))
        
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.has_vehicle)
        self.assertEqual(self.profile.vehicle_model, VEHICLE_MODEL)
        self.assertEqual(self.profile.vehicle_year, 2020)
        self.assertEqual(self.profile.vehicle_color, VEHICLE_COLOR)

    def test_preferences_settings_update(self):
        """Verifica que se pueden actualizar las preferencias de viaje"""
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        
        prefs_data = {
            FIELD_SETTINGS_TYPE: SETTINGS_TYPE_PREFERENCES,
            FIELD_PREF_MUSIC: TEST_MUSIC_POP,
            FIELD_PREF_TALK: TEST_TALK_QUIET,
            FIELD_PREF_PETS: ON_VALUE,
            FIELD_PREF_SMOKING: ON_VALUE
        }
        
        response = self.client.post(reverse(URL_SETTINGS), prefs_data)
        self.assertEqual(response.status_code, 200)
        
        messages = list(response.context[CONTEXT_MESSAGES])
        self.assertTrue(any(MSG_PREFERENCES_UPDATED in str(msg) for msg in messages))
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.pref_music, TEST_MUSIC_POP)
        self.assertEqual(self.profile.pref_talk, TEST_TALK_QUIET)
        self.assertTrue(self.profile.pref_pets)
        self.assertTrue(self.profile.pref_smoking)