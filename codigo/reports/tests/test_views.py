# ==========================================
# Autor: David Colás Martín
# ==========================================
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from reports.models import Report
from reports.tests.test_constants import *
from rides.models import Ride


class ReportViewsTests(TestCase):
    """Pruebas para las vistas de reportes."""

    def setUp(self):
        """Configura datos iniciales para las pruebas."""
        print("\nConfigurando pruebas para las vistas de reportes...")

        self.client = Client()

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

        print(f"Creados {Report.objects.count()} reportes para pruebas de vistas.")

    def test_report_list_view_admin(self):
        """Prueba que un administrador puede ver todos los reportes."""
        print("\nProbando vista de lista de reportes (admin)...")

        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        response = self.client.get(reverse(URL_REPORT_LIST))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_REPORT_LIST)

        # El admin debe ver todos los reportes
        self.assertEqual(len(response.context["reports"]), 2)

    def test_report_list_view_user(self):
        """Prueba que un usuario regular sólo ve sus propios reportes."""
        print("\nProbando vista de lista de reportes (usuario)...")

        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get(reverse(URL_REPORT_LIST))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_REPORT_LIST)

        # El usuario debe ver solo sus reportes
        self.assertEqual(len(response.context["reports"]), 1)
        self.assertEqual(response.context["reports"][0].user, self.regular_user)

    def test_report_detail_view(self):
        """Prueba que se puede ver el detalle de un reporte."""
        print("\nProbando vista de detalle de reporte...")

        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get(
            reverse(URL_REPORT_DETAIL, args=[self.user_report.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_REPORT_DETAIL)
        self.assertEqual(response.context["report"], self.user_report)

    def test_report_detail_forbidden(self):
        """Prueba que no se puede ver el reporte de otro usuario si no eres admin."""
        print("\nProbando restricción de acceso a reporte ajeno...")

        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get(
            reverse(URL_REPORT_DETAIL, args=[self.ride_report.id])
        )

        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_create_report_view(self):
        """Prueba la creación de un nuevo reporte."""
        print("\nProbando creación de reporte...")

        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)

        report_data = {
            "title": UPDATED_TITLE,
            "description": UPDATED_DESCRIPTION,
            "report_type": REPORT_TYPE_USER,
            "importance": IMPORTANCE_NORMAL,
        }

        response = self.client.post(
            reverse(URL_CREATE_REPORT) + f"?user_id={self.other_user.id}", report_data
        )

        # Debería redirigir después de crear
        self.assertEqual(response.status_code, 302)

        # Verificar que el reporte se creó
        report = Report.objects.filter(title=UPDATED_TITLE).first()
        self.assertIsNotNone(report)
        self.assertEqual(report.description, UPDATED_DESCRIPTION)
        self.assertEqual(report.user, self.regular_user)
        self.assertEqual(report.reported_user, self.other_user)

    def test_update_report_view(self):
        """Prueba la actualización de un reporte existente."""
        print("\nProbando actualización de reporte...")

        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)

        update_data = {
            "title": UPDATED_TITLE,
            "description": UPDATED_DESCRIPTION,
            "report_type": REPORT_TYPE_USER,
            "importance": IMPORTANCE_IMPORTANT,
        }

        response = self.client.post(
            reverse(URL_UPDATE_REPORT, args=[self.user_report.id]), update_data
        )

        # Debería redirigir después de actualizar
        self.assertEqual(response.status_code, 302)

        # Verificar que el reporte se actualizó
        self.user_report.refresh_from_db()
        self.assertEqual(self.user_report.title, UPDATED_TITLE)
        self.assertEqual(self.user_report.description, UPDATED_DESCRIPTION)
        self.assertEqual(self.user_report.importance, IMPORTANCE_IMPORTANT)

    def test_delete_report_view(self):
        """Prueba la eliminación de un reporte."""
        print("\nProbando eliminación de reporte...")

        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)

        response = self.client.post(
            reverse(URL_DELETE_REPORT, args=[self.user_report.id])
        )

        # Debería redirigir después de eliminar
        self.assertEqual(response.status_code, 302)

        # Verificar que el reporte se eliminó
        with self.assertRaises(Report.DoesNotExist):
            Report.objects.get(id=self.user_report.id)

    def test_mark_as_read_unread_views(self):
        """Prueba marcar reportes como leídos/no leídos."""
        print("\nProbando marcar reporte como leído/no leído...")

        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)

        # Marcar como leído
        response = self.client.get(reverse(URL_MARK_READ, args=[self.user_report.id]))
        self.assertEqual(response.status_code, 302)

        self.user_report.refresh_from_db()
        self.assertTrue(self.user_report.read)

        # Marcar como no leído
        response = self.client.get(reverse(URL_MARK_UNREAD, args=[self.user_report.id]))
        self.assertEqual(response.status_code, 302)

        self.user_report.refresh_from_db()
        self.assertFalse(self.user_report.read)

    def test_mark_as_read_unread_forbidden(self):
        """Prueba que solo los admins pueden marcar reportes como leídos/no leídos."""
        print("\nProbando restricción para marcar leído/no leído...")

        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)

        response = self.client.get(reverse(URL_MARK_READ, args=[self.user_report.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden
