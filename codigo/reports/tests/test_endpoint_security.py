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


class ReportEndpointSecurityTests(TestCase):
    """
    Pruebas de seguridad para los endpoints del módulo de reportes.
    """

    def setUp(self):
        """
        Configura los datos iniciales para las pruebas de seguridad.
        """
        print("\nConfigurando pruebas de seguridad para endpoints de reportes...")

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

        self.system_report = Report.objects.create(
            title=REPORT_TITLE,
            description=REPORT_DESCRIPTION,
            report_type=REPORT_TYPE_SYSTEM,
            importance=IMPORTANCE_URGENT,
            user=self.regular_user,
        )

        # Crear un reporte con respuesta
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

        print(f"Creados {Report.objects.count()} reportes para pruebas de seguridad.")

    def test_unauthorized_access_to_report_list(self):
        """
        Prueba que un usuario no autenticado no puede acceder a la lista de reportes.
        """
        print("\nProbando acceso no autorizado a lista de reportes...")

        # Intentar acceder sin autenticación
        response = self.client.get(reverse(URL_REPORT_LIST))

        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertTrue("/login/" in response.url)

    def test_unauthorized_access_to_report_detail(self):
        """
        Prueba que un usuario no autenticado no puede acceder al detalle de un reporte.
        """
        print("\nProbando acceso no autorizado a detalle de reporte...")

        # Intentar acceder sin autenticación
        response = self.client.get(
            reverse(URL_REPORT_DETAIL, args=[self.user_report.id])
        )

        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertTrue("/login/" in response.url)

    def test_unauthorized_user_access_to_others_report(self):
        """
        Prueba que un usuario regular no puede ver reportes de otros usuarios.
        """
        print("\nProbando acceso de usuario no autorizado a reporte ajeno...")

        # Login como other_user
        self.client.login(username=OTHER_USERNAME, password=OTHER_PASSWORD)

        # Intentar ver el detalle de un reporte de regular_user
        response = self.client.get(
            reverse(URL_REPORT_DETAIL, args=[self.user_report.id])
        )

        # Debe dar error de permiso (403 o redirección)
        self.assertIn(response.status_code, [403, 302])

    def test_admin_access_to_any_report(self):
        """
        Prueba que un administrador puede ver cualquier reporte.
        """
        print("\nProbando acceso de administrador a cualquier reporte...")

        # Login como administrador
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)

        # Intentar ver el detalle del reporte de regular_user
        response = self.client.get(
            reverse(URL_REPORT_DETAIL, args=[self.user_report.id])
        )

        # Debe permitir el acceso
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["report"], self.user_report)

    def test_unauthorized_update_of_others_report(self):
        """
        Prueba que un usuario no puede actualizar reportes de otros usuarios.
        """
        print("\nProbando actualización no autorizada de reporte ajeno...")

        # Login como other_user
        self.client.login(username=OTHER_USERNAME, password=OTHER_PASSWORD)

        # Intentar actualizar el reporte de regular_user
        update_data = {
            "title": UPDATED_TITLE,
            "description": UPDATED_DESCRIPTION,
            "report_type": REPORT_TYPE_USER,
            "importance": IMPORTANCE_IMPORTANT,
        }
        response = self.client.post(
            reverse(URL_UPDATE_REPORT, args=[self.user_report.id]), update_data
        )

        # Debe dar error de permiso (403 o redirección)
        self.assertIn(response.status_code, [403, 302])

        # Verificar que el reporte no cambió
        self.user_report.refresh_from_db()
        self.assertEqual(self.user_report.title, REPORT_TITLE)
        self.assertEqual(self.user_report.importance, IMPORTANCE_NORMAL)

    def test_unauthorized_delete_of_others_report(self):
        """
        Prueba que un usuario no puede eliminar reportes de otros usuarios.
        """
        print("\nProbando eliminación no autorizada de reporte ajeno...")

        # Login como other_user
        self.client.login(username=OTHER_USERNAME, password=OTHER_PASSWORD)

        # Intentar eliminar el reporte de regular_user
        response = self.client.post(
            reverse(URL_DELETE_REPORT, args=[self.user_report.id])
        )

        # Debe dar error de permiso (403 o redirección)
        self.assertIn(response.status_code, [403, 302])

        # Verificar que el reporte sigue existiendo
        self.assertTrue(Report.objects.filter(id=self.user_report.id).exists())

    def test_unauthorized_mark_as_read(self):
        """
        Prueba que solo los administradores pueden marcar reportes como leídos.
        """
        print("\nProbando marcado no autorizado como leído...")

        # Login como usuario regular
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)

        # Intentar marcar como leído un reporte
        response = self.client.get(reverse(URL_MARK_READ, args=[self.ride_report.id]))

        # Debe dar error de permiso (403 o redirección)
        self.assertIn(response.status_code, [403, 302])

        # Verificar que el reporte sigue no leído
        self.ride_report.refresh_from_db()
        self.assertFalse(self.ride_report.read)

    def test_unauthorized_mark_as_unread(self):
        """
        Prueba que solo los administradores pueden marcar reportes como no leídos.
        """
        print("\nProbando marcado no autorizado como no leído...")

        # Login como usuario regular
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)

        # Intentar marcar como no leído un reporte
        response = self.client.get(
            reverse(URL_MARK_UNREAD, args=[self.answered_report.id])
        )

        # Debe dar error de permiso (403 o redirección)
        self.assertIn(response.status_code, [403, 302])

        # Verificar que el reporte sigue leído
        self.answered_report.refresh_from_db()
        self.assertTrue(self.answered_report.read)

    def test_admin_mark_as_read_unread(self):
        """
        Prueba que los administradores pueden marcar reportes como leídos/no leídos.
        """
        print("\nProbando marcado de administrador como leído/no leído...")

        # Login como administrador
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)

        # Marcar como leído
        response = self.client.get(reverse(URL_MARK_READ, args=[self.ride_report.id]))
        self.assertEqual(response.status_code, 302)

        self.ride_report.refresh_from_db()
        self.assertTrue(self.ride_report.read)

        # Marcar como no leído
        response = self.client.get(reverse(URL_MARK_UNREAD, args=[self.ride_report.id]))
        self.assertEqual(response.status_code, 302)

        self.ride_report.refresh_from_db()
        self.assertFalse(self.ride_report.read)

    def test_create_report_with_invalid_data(self):
        """
        Prueba que no se pueden crear reportes con datos inválidos.
        """
        print("\nProbando creación de reporte con datos inválidos...")

        # Login como usuario regular
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)

        # Intentar crear un reporte sin título
        invalid_data = {
            "description": REPORT_DESCRIPTION,
            "report_type": REPORT_TYPE_SYSTEM,
            "importance": IMPORTANCE_NORMAL,
        }

        response = self.client.post(reverse(URL_CREATE_REPORT), invalid_data)

        # Debería mostrar el formulario de nuevo con errores
        self.assertEqual(response.status_code, 200)
        self.assertTrue("form" in response.context)
        self.assertFalse(response.context["form"].is_valid())

        # Verificar que no se creó un nuevo reporte
        self.assertEqual(Report.objects.count(), 4)  # Los 4 reportes iniciales

    def test_update_report_with_response(self):
        """
        Prueba que no se pueden actualizar reportes que ya tienen una respuesta.
        """
        print("\nProbando actualización de reporte con respuesta...")

        # Login como creador del reporte con respuesta
        self.client.login(username=OTHER_USERNAME, password=OTHER_PASSWORD)

        # Intentar actualizar el reporte que ya tiene respuesta
        update_data = {
            "title": UPDATED_TITLE,
            "description": UPDATED_DESCRIPTION,
            "report_type": REPORT_TYPE_USER,
            "importance": IMPORTANCE_IMPORTANT,
        }
        response = self.client.post(
            reverse(URL_UPDATE_REPORT, args=[self.answered_report.id]), update_data
        )

        # Debe redirigir sin actualizar
        self.assertEqual(response.status_code, 302)

        # Verificar que el reporte no cambió
        self.answered_report.refresh_from_db()
        self.assertEqual(self.answered_report.title, REPORT_TITLE)

    def test_csrf_protection(self):
        """
        Prueba que las peticiones POST están protegidas contra CSRF.
        """
        print("\nProbando protección CSRF...")

        # Login como usuario regular
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)

        # Desactivar verificación CSRF para este cliente
        self.client.handler.enforce_csrf_checks = True

        # Intentar actualizar un reporte sin token CSRF
        update_data = {
            "title": UPDATED_TITLE,
            "description": UPDATED_DESCRIPTION,
            "report_type": REPORT_TYPE_USER,
            "importance": IMPORTANCE_IMPORTANT,
        }
        response = self.client.post(
            reverse(URL_UPDATE_REPORT, args=[self.user_report.id]), update_data
        )

        # Debería fallar por falta de token CSRF
        self.assertEqual(response.status_code, 403)  # Forbidden
