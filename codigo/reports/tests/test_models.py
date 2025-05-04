# ==========================================
# Autor: David Colás Martín
# ==========================================
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from reports.models import Report
from reports.tests.test_constants import *
from rides.models import Ride


class ReportModelTests(TestCase):
    """Prueba para el modelo Report."""

    def setUp(self):
        """Configura datos iniciales para las pruebas."""
        print("\nConfigurando pruebas para el modelo Report...")

        # Crear usuarios
        self.admin_user = User.objects.create_superuser(
            username=ADMIN_USERNAME, email=ADMIN_EMAIL, password=ADMIN_PASSWORD
        )

        self.regular_user = User.objects.create_user(
            username=USER_USERNAME, email=USER_EMAIL, password=USER_PASSWORD
        )

        self.other_user = User.objects.create_user(
            username=OTHER_USERNAME, email=OTHER_EMAIL, password=OTHER_PASSWORD
        )

        # Crear viaje
        self.future_date = timezone.now() + timedelta(days=RIDE_DAYS_FUTURE)
        self.ride = Ride.objects.create(
            driver=self.regular_user,
            origin=RIDE_ORIGIN,
            destination=RIDE_DESTINATION,
            departure_time=self.future_date,
            total_seats=RIDE_SEATS,
            price=RIDE_PRICE,
        )

        # Crear reportes
        self.user_report = Report.objects.create(
            title=REPORT_TITLE,
            description=REPORT_DESCRIPTION,
            report_type=REPORT_TYPE_USER,
            importance=IMPORTANCE_NORMAL,
            user=self.regular_user,
            reported_user=self.other_user,
        )

        self.ride_report = Report.objects.create(
            title=REPORT_TITLE,
            description=REPORT_DESCRIPTION,
            report_type=REPORT_TYPE_RIDE,
            importance=IMPORTANCE_IMPORTANT,
            user=self.other_user,
            ride=self.ride,
        )

        self.system_report = Report.objects.create(
            title=REPORT_TITLE,
            description=REPORT_DESCRIPTION,
            report_type=REPORT_TYPE_SYSTEM,
            importance=IMPORTANCE_URGENT,
            user=self.regular_user,
        )

        # Crear reporte con respuesta
        self.answered_report = Report.objects.create(
            title=REPORT_TITLE,
            description=REPORT_DESCRIPTION,
            report_type=REPORT_TYPE_USER,
            importance=IMPORTANCE_NORMAL,
            user=self.other_user,
            reported_user=self.regular_user,
            response=REPORT_RESPONSE,
            response_by=self.admin_user,
            response_at=timezone.now(),
            read=True,
        )

        print(f"Creados {Report.objects.count()} reportes para pruebas.")

    def test_report_creation(self):
        """Verifica que los reportes se crean correctamente."""
        print("\nProbando la creación de reportes...")

        self.assertEqual(self.user_report.title, REPORT_TITLE)
        self.assertEqual(self.user_report.description, REPORT_DESCRIPTION)
        self.assertEqual(self.user_report.report_type, REPORT_TYPE_USER)
        self.assertEqual(self.user_report.importance, IMPORTANCE_NORMAL)
        self.assertEqual(self.user_report.user, self.regular_user)
        self.assertEqual(self.user_report.reported_user, self.other_user)
        self.assertFalse(self.user_report.read)

        self.assertEqual(self.ride_report.report_type, REPORT_TYPE_RIDE)
        self.assertEqual(self.ride_report.importance, IMPORTANCE_IMPORTANT)
        self.assertEqual(self.ride_report.ride, self.ride)

        self.assertEqual(self.system_report.report_type, REPORT_TYPE_SYSTEM)
        self.assertEqual(self.system_report.importance, IMPORTANCE_URGENT)

    def test_report_response(self):
        """Verifica que las respuestas a reportes funcionan correctamente."""
        print("\nProbando respuestas a reportes...")

        self.assertEqual(self.answered_report.response, REPORT_RESPONSE)
        self.assertEqual(self.answered_report.response_by, self.admin_user)
        self.assertIsNotNone(self.answered_report.response_at)
        self.assertTrue(self.answered_report.read)

    def test_get_absolute_url(self):
        """Verifica que get_absolute_url devuelve la URL correcta."""
        print("\nProbando get_absolute_url...")

        expected_url = f"/reports/{self.user_report.pk}/"
        self.assertTrue(self.user_report.get_absolute_url().endswith(expected_url))

    def test_string_representation(self):
        """Verifica la representación en string del modelo."""
        print("\nProbando representación en string...")

        expected = f"{REPORT_TITLE} (Usuario)"
        self.assertEqual(str(self.user_report), expected)

        expected = f"{REPORT_TITLE} (Viaje)"
        self.assertEqual(str(self.ride_report), expected)

        expected = f"{REPORT_TITLE} (Sistema)"
        self.assertEqual(str(self.system_report), expected)
