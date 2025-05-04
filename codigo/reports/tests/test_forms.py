# ==========================================
# Autor: David Colás Martín
# ==========================================
from django.contrib.auth.models import User
from django.test import TestCase
from reports.forms import ReportFilterForm, ReportForm, ReportResponseForm
from reports.models import Report
from reports.tests.test_constants import *


class ReportFormTests(TestCase):
    """Pruebas para los formularios de reportes."""

    def setUp(self):
        """Configura datos iniciales para las pruebas."""
        print("\nConfigurando pruebas para los formularios de reportes...")

        self.user = User.objects.create_user(
            username=USER_USERNAME, email=USER_EMAIL, password=USER_PASSWORD
        )

    def test_report_form_valid_data(self):
        """Prueba que el formulario acepta datos válidos."""
        print("\nProbando formulario con datos válidos...")

        form_data = {
            "title": REPORT_TITLE,
            "description": REPORT_DESCRIPTION,
            "report_type": REPORT_TYPE_SYSTEM,
            "importance": IMPORTANCE_NORMAL,
        }

        form = ReportForm(data=form_data)
        self.assertTrue(form.is_valid())

        report = form.save(commit=False)
        report.user = self.user
        report.save()

        self.assertEqual(report.title, REPORT_TITLE)
        self.assertEqual(report.description, REPORT_DESCRIPTION)
        self.assertEqual(report.report_type, REPORT_TYPE_SYSTEM)
        self.assertEqual(report.importance, IMPORTANCE_NORMAL)
        self.assertEqual(report.user, self.user)

    def test_report_form_invalid_data(self):
        """Prueba que el formulario rechaza datos inválidos."""
        print("\nProbando formulario con datos inválidos...")

        # Formulario sin título
        form_data = {
            "description": REPORT_DESCRIPTION,
            "report_type": REPORT_TYPE_SYSTEM,
            "importance": IMPORTANCE_NORMAL,
        }

        form = ReportForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_report_response_form(self):
        """Prueba el formulario de respuesta a reportes."""
        print("\nProbando formulario de respuesta...")

        # Crear un reporte para responder
        report = Report.objects.create(
            title=REPORT_TITLE,
            description=REPORT_DESCRIPTION,
            report_type=REPORT_TYPE_SYSTEM,
            importance=IMPORTANCE_NORMAL,
            user=self.user,
        )

        form_data = {"response": REPORT_RESPONSE}

        form = ReportResponseForm(data=form_data, instance=report)
        self.assertTrue(form.is_valid())

        saved_report = form.save()
        self.assertEqual(saved_report.response, REPORT_RESPONSE)

    def test_report_filter_form(self):
        """Prueba el formulario de filtrado de reportes."""
        print("\nProbando formulario de filtrado...")

        form_data = {
            "report_type": REPORT_TYPE_USER,
            "importance": IMPORTANCE_IMPORTANT,
            "read": True,
            "search": "texto de búsqueda",
        }

        form = ReportFilterForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["report_type"], REPORT_TYPE_USER)
        self.assertEqual(form.cleaned_data["importance"], IMPORTANCE_IMPORTANT)
        self.assertTrue(form.cleaned_data["read"])
        self.assertEqual(form.cleaned_data["search"], "texto de búsqueda")
