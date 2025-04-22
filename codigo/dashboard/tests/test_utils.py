# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================


"""
Pruebas para las utilidades del dashboard.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime
import json

from rides.models import Ride
from reports.models import Report
from accounts.models import UserProfile
from dashboard._utils import (
    get_date_range_for_period, get_date_range,
    get_last_n_days, get_hourly_labels, get_daily_labels,
    get_monthly_labels, get_dashboard_data, get_rides_data,
    get_messages_data, get_reports_data, get_users_data,
    get_payments_data, serialize_dashboard_data
)
from dashboard.tests.test_constants import *

class DashboardUtilsTests(TestCase):
    """Pruebas para las funciones de utilidad del dashboard."""
    
    def setUp(self):
        """Configura los datos iniciales para las pruebas."""
        print("\nConfigurando pruebas para las utilidades del dashboard...")
        
        
        self.admin_user = User.objects.create_superuser(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD
        )
        UserProfile.objects.create(user=self.admin_user)
        
        self.regular_user = User.objects.create_user(
            username=REGULAR_USERNAME,
            email=REGULAR_EMAIL,
            password=REGULAR_PASSWORD
        )
        UserProfile.objects.create(user=self.regular_user)
        
        
        self.future_date = timezone.now() + timedelta(days=DAYS_FUTURE)
        self.past_date = timezone.now() - timedelta(days=DAYS_PAST)
        
        self.future_ride = Ride.objects.create(
            driver=self.regular_user,
            origin=TEST_ORIGIN,
            destination=TEST_DESTINATION,
            departure_time=self.future_date,
            total_seats=TEST_SEATS,
            price=TEST_PRICE
        )
        
        self.past_ride = Ride.objects.create(
            driver=self.regular_user,
            origin=TEST_DESTINATION,
            destination=TEST_ORIGIN,
            departure_time=self.past_date,
            total_seats=TEST_SEATS,
            price=TEST_PRICE
        )
        
        print("Se han creado los datos para las pruebas de utilidades del dashboard.")
    
    def test_get_date_range_for_period(self):
        """Prueba la función para obtener rangos de fecha según el período."""
        print("\nProbando get_date_range_for_period...")
        
        
        start_date, end_date, period_text = get_date_range_for_period(TEST_PERIOD_TODAY)
        self.assertEqual(start_date.date(), timezone.now().date())
        self.assertTrue(end_date <= timezone.now())
        
        
        start_date, end_date, period_text = get_date_range_for_period(TEST_PERIOD_WEEK)
        self.assertTrue((timezone.now() - start_date).days <= 7)
        self.assertTrue(end_date <= timezone.now())
        
        
        start_date, end_date, period_text = get_date_range_for_period(TEST_PERIOD_MONTH)
        self.assertTrue((timezone.now() - start_date).days <= 30)
        self.assertTrue(end_date <= timezone.now())
        
        
        start_date, end_date, period_text = get_date_range_for_period(TEST_PERIOD_YEAR)
        self.assertTrue((timezone.now() - start_date).days <= 365)
        self.assertTrue(end_date <= timezone.now())
        
        
        start_date, end_date, period_text = get_date_range_for_period(TEST_PERIOD_ALL)
        self.assertTrue(start_date.year <= 1970)
        self.assertTrue(end_date <= timezone.now())
    
    def test_get_date_range(self):
        """Prueba la función para obtener rangos de fecha."""
        print("\nProbando get_date_range...")
        
        
        start_date, end_date = get_date_range(TEST_PERIOD_TODAY)
        self.assertEqual(start_date, timezone.now().date())
        self.assertEqual(end_date, timezone.now().date())
        
        
        start_date, end_date = get_date_range(TEST_PERIOD_WEEK)
        self.assertTrue((end_date - start_date).days <= 7)
        self.assertEqual(end_date, timezone.now().date())
        
        
        start_date, end_date = get_date_range(TEST_PERIOD_ALL)
        self.assertIsNone(start_date)
        self.assertEqual(end_date, timezone.now().date())
    
    def test_get_last_n_days(self):
        """Prueba la función para obtener los últimos n días."""
        print("\nProbando get_last_n_days...")
        
        days = get_last_n_days(7)
        self.assertEqual(len(days), 7)
        
        days = get_last_n_days(30)
        self.assertEqual(len(days), 30)
        
        
        for day in days:
            self.assertTrue('/' in day)
    
    def test_get_hourly_labels(self):
        """Prueba la función para obtener etiquetas horarias."""
        print("\nProbando get_hourly_labels...")
        
        labels = get_hourly_labels(timezone.now().date())
        self.assertEqual(len(labels), 24)
        self.assertEqual(labels[0], "00:00")
        self.assertEqual(labels[23], "23:00")
    
    def test_get_daily_labels(self):
        """Prueba la función para obtener etiquetas diarias."""
        print("\nProbando get_daily_labels...")
        
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        labels = get_daily_labels(week_ago, today)
        self.assertEqual(len(labels), 8)  
    
    def test_get_monthly_labels(self):
        """Prueba la función para obtener etiquetas mensuales."""
        print("\nProbando get_monthly_labels...")
        
        today = timezone.now().date()
        year_ago = today - timedelta(days=365)
        
        labels = get_monthly_labels(year_ago, today)
        
        self.assertTrue(len(labels) >= 12)
        
        
        for month in labels:
            self.assertTrue(' ' in month)  
    
    def test_serialize_dashboard_data(self):
        """Prueba la función para serializar datos del dashboard."""
        print("\nProbando serialize_dashboard_data...")
        
        test_data = {
            'string': 'test',
            'number': 123,
            'date': timezone.now(),
            'nested': {'key': 'value'}
        }
        
        serialized = serialize_dashboard_data(test_data)
        self.assertIsInstance(serialized, str)
        
        
        deserialized = json.loads(serialized)
        self.assertEqual(deserialized['string'], 'test')
        self.assertEqual(deserialized['number'], 123)
        self.assertIn('nested', deserialized)
        self.assertEqual(deserialized['nested']['key'], 'value')
    
    def test_get_dashboard_data(self):
        """Prueba la función para obtener datos del dashboard."""
        print("\nProbando get_dashboard_data...")
        
        context = get_dashboard_data(TEST_PERIOD_WEEK)
        
        
        self.assertIn('time_period', context)
        self.assertIn('available_periods', context)
        self.assertIn('chart_colors', context)
        self.assertIn('trip_data', context)
        self.assertIn('msg_data', context)
        self.assertIn('report_data', context)
        self.assertIn('user_data', context)
        self.assertIn('payment_data', context)
        
        
        self.assertEqual(context['time_period'], TEST_PERIOD_WEEK)
    
    def test_get_rides_data(self):
        """Prueba la función para obtener datos de viajes."""
        print("\nProbando get_rides_data...")
        
        for period in [TEST_PERIOD_TODAY, TEST_PERIOD_WEEK, TEST_PERIOD_MONTH, TEST_PERIOD_YEAR, TEST_PERIOD_ALL]:
            data = get_rides_data(period)
            self.assertIn('active_rides', data)
            self.assertIn('completed_rides', data)
            self.assertIn('total_rides', data)
    
    def test_get_messages_data(self):
        """Prueba la función para obtener datos de mensajes."""
        print("\nProbando get_messages_data...")
        
        
        for period in [TEST_PERIOD_TODAY, TEST_PERIOD_WEEK, TEST_PERIOD_MONTH, TEST_PERIOD_YEAR, TEST_PERIOD_ALL]:
            data = get_messages_data(period)
            self.assertIn('total', data)
            self.assertIn('labels', data)
            self.assertIn('data', data)
            self.assertIn('avg_per_day', data)
    
    def test_get_reports_data(self):
        """Prueba la función para obtener datos de reportes."""
        print("\nProbando get_reports_data...")
        
        
        for period in [TEST_PERIOD_TODAY, TEST_PERIOD_WEEK, TEST_PERIOD_MONTH, TEST_PERIOD_YEAR, TEST_PERIOD_ALL]:
            data = get_reports_data(period)
            self.assertIn('total', data)
            self.assertIn('unread', data)
            self.assertIn('resolved', data)
            self.assertIn('labels', data)
    
    def test_get_users_data(self):
        """Prueba la función para obtener datos de usuarios."""
        print("\nProbando get_users_data...")
        
        
        for period in [TEST_PERIOD_TODAY, TEST_PERIOD_WEEK, TEST_PERIOD_MONTH, TEST_PERIOD_YEAR, TEST_PERIOD_ALL]:
            data = get_users_data(period)
            self.assertIn('total', data)
            self.assertIn('active', data)
            self.assertIn('inactive', data)
            self.assertIn('with_vehicle', data)
            self.assertIn('labels', data)
    
    def test_get_payments_data(self):
        """Prueba la función para obtener datos de pagos."""
        print("\nProbando get_payments_data...")
        
        
        for period in [TEST_PERIOD_TODAY, TEST_PERIOD_WEEK, TEST_PERIOD_MONTH, TEST_PERIOD_YEAR, TEST_PERIOD_ALL]:
            data = get_payments_data(period)
            self.assertIn('total', data)
            self.assertIn('amount', data)
            self.assertIn('avg_per_transaction', data)
            self.assertIn('labels', data)