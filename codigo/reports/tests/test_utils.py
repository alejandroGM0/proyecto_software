# ==========================================
# Autor: David Colás Martín
# ==========================================
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.http import Http404, HttpResponseForbidden
from django.test import RequestFactory, TestCase
from django.utils import timezone
from reports import _utils
from reports.forms import ReportFilterForm
from reports.models import Report
from reports.tests.test_constants import *


class ReportUtilsTests(TestCase):
    """Pruebas para las funciones de utilidad del módulo de reportes."""

    def setUp(self):
        """Configura los datos iniciales para las pruebas."""
        print("\nConfigurando pruebas para las funciones de utilidad...")

        self.factory = RequestFactory()

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

        # Crear reportes
        self.user_report = Report.objects.create(
            title=REPORT_TITLE,
            description=REPORT_DESCRIPTION,
            report_type=REPORT_TYPE_USER,
            importance=IMPORTANCE_NORMAL,
            user=self.regular_user,
            reported_user=self.other_user,
        )

        print(f"Creados {Report.objects.count()} reportes para pruebas de utilidades.")

    @patch("reports._utils.get_object_or_404")
    def test_get_report_or_404(self, mock_get_object):
        """Prueba la función get_report_or_404."""
        print("\nProbando get_report_or_404...")

        mock_get_object.return_value = self.user_report
        report = _utils.get_report_or_404(1)

        self.assertEqual(report, self.user_report)
        mock_get_object.assert_called_once_with(Report, pk=1)

    def test_check_report_view_permission(self):
        """Prueba la función check_report_view_permission."""
        print("\nProbando check_report_view_permission...")

        # Crear requests simulados
        admin_request = self.factory.get("/")
        admin_request.user = self.admin_user

        owner_request = self.factory.get("/")
        owner_request.user = self.regular_user

        other_request = self.factory.get("/")
        other_request.user = self.other_user

        # Probar permisos
        self.assertIsNone(
            _utils.check_report_view_permission(admin_request, self.user_report)
        )
        self.assertIsNone(
            _utils.check_report_view_permission(owner_request, self.user_report)
        )
        self.assertIsInstance(
            _utils.check_report_view_permission(other_request, self.user_report),
            HttpResponseForbidden,
        )

    @patch("reports._utils.messages")
    def test_check_report_edit_permission(self, mock_messages):
        """Prueba la función check_report_edit_permission."""
        print("\nProbando check_report_edit_permission...")

        # Crear requests simulados
        admin_request = self.factory.get("/")
        admin_request.user = self.admin_user

        owner_request = self.factory.get("/")
        owner_request.user = self.regular_user

        other_request = self.factory.get("/")
        other_request.user = self.other_user

        # Probar permisos
        self.assertIsNone(
            _utils.check_report_edit_permission(admin_request, self.user_report)
        )
        self.assertIsNone(
            _utils.check_report_edit_permission(owner_request, self.user_report)
        )
        self.assertIsInstance(
            _utils.check_report_edit_permission(other_request, self.user_report),
            HttpResponseForbidden,
        )

        # Añadir respuesta al reporte y probar nuevamente
        self.user_report.response = "Respuesta de prueba"
        self.user_report.save()

        # Admin sigue pudiendo editar, pero el propietario ya no
        self.assertIsNone(
            _utils.check_report_edit_permission(admin_request, self.user_report)
        )

        # Para la redirección cuando hay respuesta, mockear el método redirect
        with patch("reports._utils.redirect") as mock_redirect:
            mock_redirect.return_value = "REDIRECT_RESULT"
            result = _utils.check_report_edit_permission(
                owner_request, self.user_report
            )
            self.assertEqual(result, "REDIRECT_RESULT")
            mock_messages.warning.assert_called_once()

    def test_filter_reports(self):
        """Prueba la función filter_reports."""
        print("\nProbando filter_reports...")

        # Crear reportes adicionales para filtrado
        Report.objects.create(
            title="Reporte importante",
            description="Descripción del reporte importante",
            report_type=REPORT_TYPE_SYSTEM,
            importance=IMPORTANCE_IMPORTANT,
            user=self.regular_user,
        )

        Report.objects.create(
            title="Reporte urgente",
            description="Descripción del reporte urgente",
            report_type=REPORT_TYPE_SYSTEM,
            importance=IMPORTANCE_URGENT,
            user=self.regular_user,
            read=True,
        )

        all_reports = Report.objects.all()

        # Filtrar por tipo
        request = self.factory.get("/", {"report_type": REPORT_TYPE_USER})
        filtered, _ = _utils.filter_reports(request, all_reports)
        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.user_report)

        # Filtrar por importancia
        request = self.factory.get("/", {"importance": IMPORTANCE_URGENT})
        filtered, _ = _utils.filter_reports(request, all_reports)
        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first().importance, IMPORTANCE_URGENT)

        # Filtrar por no leídos
        request = self.factory.get("/", {"read": "true"})
        filtered, _ = _utils.filter_reports(request, all_reports)
        self.assertEqual(filtered.count(), 2)  # Los que NO están marcados como leídos

        # Filtrar por búsqueda
        request = self.factory.get("/", {"search": "urgente"})
        filtered, _ = _utils.filter_reports(request, all_reports)
        self.assertEqual(filtered.count(), 1)
        self.assertTrue(
            "urgente" in filtered.first().title.lower()
            or "urgente" in filtered.first().description.lower()
        )

    def test_paginate_reports(self):
        """Prueba la función paginate_reports."""
        print("\nProbando paginate_reports...")

        # Crear reportes adicionales para tener suficientes para paginar
        for i in range(15):  # Crear 15 reportes más
            Report.objects.create(
                title=f"Reporte {i}",
                description=f"Descripción del reporte {i}",
                report_type=REPORT_TYPE_SYSTEM,
                importance=IMPORTANCE_NORMAL,
                user=self.regular_user,
            )

        all_reports = Report.objects.all()

        # Página 1
        request = self.factory.get("/")
        page_obj = _utils.paginate_reports(request, all_reports)
        self.assertEqual(len(page_obj), 10)  # Límite por página

        # Página 2
        request = self.factory.get("/", {"page": 2})
        page_obj = _utils.paginate_reports(request, all_reports)
        self.assertEqual(
            len(page_obj), 6
        )  # 16 reportes en total, 6 en la segunda página
