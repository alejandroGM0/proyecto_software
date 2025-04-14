from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from accounts._utils import create_stripe_onboarding_link, create_stripe_connect_account
from accounts.models import UserProfile

class StripeUtilsTests(TestCase):
    """
    Pruebas para utilidades de Stripe Connect (onboarding y validación de correo).
    """
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        UserProfile.objects.create(user=self.user)
        self.user_no_email = User.objects.create_user('nouser', '', 'testpass')
        UserProfile.objects.create(user=self.user_no_email)
        self.user.profile.stripe_account_id = 'acct_test_123'
        self.user.profile.save()

    @patch('accounts._utils.stripe.AccountLink.create')
    def test_create_stripe_onboarding_link_ok(self, mock_create):
        mock_create.return_value = MagicMock(url='https://onboarding.test/')
        url = create_stripe_onboarding_link(self.user)
        self.assertEqual(url, 'https://onboarding.test/')

    def test_create_stripe_onboarding_link_no_account(self):
        self.user.profile.stripe_account_id = ''
        self.user.profile.save()
        url = create_stripe_onboarding_link(self.user)
        self.assertIsNone(url)

    @patch('accounts._utils.stripe.Account.create')
    @patch('accounts._utils.stripe.Account.list')
    def test_create_stripe_connect_account_no_email(self, mock_list, mock_create):
        # No debe crear cuenta si el usuario no tiene email
        result = create_stripe_connect_account(self.user_no_email)
        self.assertIsNone(result)

    @patch('accounts._utils.stripe.Account.create')
    @patch('accounts._utils.stripe.Account.list')
    def test_create_stripe_connect_account_ok(self, mock_list, mock_create):
        mock_create.return_value = MagicMock(id='acct_test_ok')
        result = create_stripe_connect_account(self.user)
        self.assertEqual(result, 'acct_test_ok')
