# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date

from accounts.models import UserProfile
from accounts.tests.test_constants import *

class UserProfileModelTests(TestCase):
    """Pruebas para el modelo UserProfile"""

    def setUp(self):
        """Configura un usuario y un perfil para las pruebas"""
        self.user = User.objects.create_user(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD
        )

        self.profile = UserProfile.objects.create(
            user=self.user,
            bio=TEST_BIO,
            phone_number=TEST_PHONE,
            location=TEST_LOCATION,
            birth_date=date(TEST_BIRTH_YEAR, TEST_BIRTH_MONTH, TEST_BIRTH_DAY),
            has_vehicle=True,
            vehicle_model=TEST_VEHICLE_MODEL,
            vehicle_year=TEST_VEHICLE_YEAR,
            vehicle_color=TEST_VEHICLE_COLOR,
            pref_music=TEST_MUSIC,
            pref_talk=TEST_TALK,
            pref_pets=True
        )

    def test_profile_creation(self):
        """Verifica que el perfil se crea correctamente"""
        self.assertEqual(self.profile.user.username, TEST_USERNAME)
        self.assertEqual(self.profile.bio, TEST_BIO)
        self.assertEqual(self.profile.has_vehicle, True)
        self.assertEqual(self.profile.vehicle_model, TEST_VEHICLE_MODEL)

    def test_profile_string_representation(self):
        """Verifica la representación en cadena del perfil"""
        expected_string = PROFILE_STRING_FORMAT.format(self.user.username)
        self.assertEqual(str(self.profile), expected_string)

    def test_get_age(self):
        """Verifica que el método get_age funciona correctamente"""
        expected_age = timezone.now().date().year - TEST_BIRTH_YEAR
        today = timezone.now().date()
        if (today.month, today.day) < (TEST_BIRTH_MONTH, TEST_BIRTH_DAY): 
            expected_age -= 1

        self.assertEqual(self.profile.get_age(), expected_age)

    def test_get_activity_status(self):
        """Verifica que el estado de actividad se determina correctamente"""
        self.assertEqual(self.profile.get_activity_status(), STATUS_ONLINE)

        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE accounts_userprofile SET last_active = %s WHERE id = %s",
                [(timezone.now() - timedelta(days=DAYS_OFFLINE)).isoformat(), self.profile.id]
            )
        
        self.profile = UserProfile.objects.get(id=self.profile.id)
        self.assertEqual(self.profile.get_activity_status(), STATUS_DAYS)
        
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE accounts_userprofile SET last_active = %s WHERE id = %s",
                [(timezone.now() - timedelta(days=WEEKS_OFFLINE)).isoformat(), self.profile.id]
            )
        
        self.profile = UserProfile.objects.get(id=self.profile.id)
        self.assertEqual(self.profile.get_activity_status(), STATUS_WEEKS)