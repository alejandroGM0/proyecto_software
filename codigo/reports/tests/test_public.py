from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from reports.models import Report
from rides.models import Ride
from reports import public
from reports.tests.test_constants import *

class ReportPublicAPITests(TestCase):
    """Pruebas para las funciones públicas del módulo de reportes."""
    
    def setUp(self):
        """Configura los datos iniciales para las pruebas."""
        print("\nConfigurando pruebas para el API público de reportes...")
        
        # Crear usuarios
        self.admin_user = User.objects.create_superuser(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD
        )
        
        self.regular_user = User.objects.create_user(
            username=USER_USERNAME,
            email=USER_EMAIL,
            password=USER_PASSWORD
        )
        
        self.other_user = User.objects.create_user(
            username=OTHER_USERNAME,
            email=OTHER_EMAIL,
            password=OTHER_PASSWORD
        )
        
        # Crear viaje
        self.future_date = timezone.now() + timedelta(days=RIDE_DAYS_FUTURE)
        self.ride = Ride.objects.create(
            driver=self.regular_user,
            origin=RIDE_ORIGIN,
            destination=RIDE_DESTINATION,
            departure_time=self.future_date,
            total_seats=RIDE_SEATS,
            price=RIDE_PRICE
        )
        
        # Crear reportes
        self.user_report = Report.objects.create(
            title=REPORT_TITLE,
            description=REPORT_DESCRIPTION,
            report_type=REPORT_TYPE_USER,
            importance=IMPORTANCE_NORMAL,
            user=self.regular_user,
            reported_user=self.other_user
        )
        
        self.ride_report = Report.objects.create(
            title=REPORT_TITLE,
            description=REPORT_DESCRIPTION,
            report_type=REPORT_TYPE_RIDE,
            importance=IMPORTANCE_IMPORTANT,
            user=self.other_user,
            ride=self.ride
        )
        
        print(f"Creados {Report.objects.count()} reportes para pruebas de API público.")
    
    def test_get_report_by_id(self):
        """Prueba la obtención de reporte por ID."""
        print("\nProbando get_report_by_id...")
        
        report = public.get_report_by_id(self.user_report.id)
        self.assertEqual(report, self.user_report)
        
        # Prueba con ID inexistente
        report = public.get_report_by_id(99999)
        self.assertIsNone(report)
    
    def test_get_user_reports(self):
        """Prueba la obtención de reportes de un usuario."""
        print("\nProbando get_user_reports...")
        
        reports = public.get_user_reports(self.regular_user)
        self.assertEqual(reports.count(), 1)
        self.assertEqual(reports.first(), self.user_report)
    
    def test_get_reports_about_user(self):
        """Prueba la obtención de reportes sobre un usuario."""
        print("\nProbando get_reports_about_user...")
        
        reports = public.get_reports_about_user(self.other_user)
        self.assertEqual(reports.count(), 1)
        self.assertEqual(reports.first(), self.user_report)
    
    def test_get_reports_about_ride(self):
        """Prueba la obtención de reportes sobre un viaje."""
        print("\nProbando get_reports_about_ride...")
        
        reports = public.get_reports_about_ride(self.ride)
        self.assertEqual(reports.count(), 1)
        self.assertEqual(reports.first(), self.ride_report)
    
    def test_get_reports_by_type(self):
        """Prueba la obtención de reportes por tipo."""
        print("\nProbando get_reports_by_type...")
        
        reports = public.get_reports_by_type(REPORT_TYPE_USER)
        self.assertEqual(reports.count(), 1)
        self.assertEqual(reports.first(), self.user_report)
    
    def test_get_reports_by_importance(self):
        """Prueba la obtención de reportes por importancia."""
        print("\nProbando get_reports_by_importance...")
        
        reports = public.get_reports_by_importance(IMPORTANCE_IMPORTANT)
        self.assertEqual(reports.count(), 1)
        self.assertEqual(reports.first(), self.ride_report)
    
    def test_search_reports(self):
        """Prueba la búsqueda de reportes."""
        print("\nProbando search_reports...")
        
        # Crear un reporte con texto distintivo
        distinctive_report = Report.objects.create(
            title="Reporte único",
            description="Descripción única para búsqueda",
            report_type=REPORT_TYPE_SYSTEM,
            importance=IMPORTANCE_NORMAL,
            user=self.regular_user
        )
        
        reports = public.search_reports("único")
        self.assertEqual(reports.count(), 1)
        self.assertEqual(reports.first(), distinctive_report)
    
    def test_permissions(self):
        """Prueba las funciones de verificación de permisos."""
        print("\nProbando funciones de permisos...")
        
        # can_view_report
        self.assertTrue(public.can_view_report(self.admin_user, self.user_report))
        self.assertTrue(public.can_view_report(self.regular_user, self.user_report))
        self.assertFalse(public.can_view_report(self.other_user, self.user_report))
        
        # can_edit_report
        self.assertTrue(public.can_edit_report(self.admin_user, self.user_report))
        self.assertTrue(public.can_edit_report(self.regular_user, self.user_report))
        self.assertFalse(public.can_edit_report(self.other_user, self.user_report))
        
        # can_delete_report
        self.assertTrue(public.can_delete_report(self.admin_user, self.user_report))
        self.assertTrue(public.can_delete_report(self.regular_user, self.user_report))
        self.assertFalse(public.can_delete_report(self.other_user, self.user_report))
    
    def test_respond_to_report(self):
        """Prueba la función de responder a reportes."""
        print("\nProbando respond_to_report...")
        
        # Admin puede responder
        result = public.respond_to_report(self.admin_user, self.user_report, "Respuesta de prueba")
        self.assertTrue(result)
        
        self.user_report.refresh_from_db()
        self.assertEqual(self.user_report.response, "Respuesta de prueba")
        self.assertEqual(self.user_report.response_by, self.admin_user)
        self.assertIsNotNone(self.user_report.response_at)
        self.assertTrue(self.user_report.read)
        
        # Usuario regular no puede responder
        result = public.respond_to_report(self.regular_user, self.ride_report, "Intento de respuesta")
        self.assertFalse(result)
        
        self.ride_report.refresh_from_db()
        self.assertIsNone(self.ride_report.response)
    
    def test_create_report_functions(self):
        """Prueba las funciones para crear distintos tipos de reportes."""
        print("\nProbando funciones de creación de reportes...")
        
        # crear_user_report
        user_report = public.create_user_report(
            self.regular_user, 
            self.other_user, 
            "Nuevo reporte de usuario", 
            "Descripción del reporte", 
            IMPORTANCE_URGENT
        )
        
        self.assertEqual(user_report.report_type, REPORT_TYPE_USER)
        self.assertEqual(user_report.user, self.regular_user)
        self.assertEqual(user_report.reported_user, self.other_user)
        self.assertEqual(user_report.importance, IMPORTANCE_URGENT)
        
        # crear_ride_report
        ride_report = public.create_ride_report(
            self.regular_user,
            self.ride,
            "Nuevo reporte de viaje",
            "Descripción del reporte"
        )
        
        self.assertEqual(ride_report.report_type, REPORT_TYPE_RIDE)
        self.assertEqual(ride_report.user, self.regular_user)
        self.assertEqual(ride_report.ride, self.ride)
        self.assertEqual(ride_report.importance, IMPORTANCE_NORMAL)  # Valor por defecto
