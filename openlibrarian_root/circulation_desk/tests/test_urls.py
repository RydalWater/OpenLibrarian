from django.test import TestCase
from django.urls import reverse

# Unit tests for forms
class TestUrls(TestCase):
    """
    Unit tests for app urls
    """
    def setUp(self):
        pass
    
    def test_index_url(self):
        """
        Test index url in Circulation Desk
        """
        url = reverse('circulation_desk:index')
        self.assertEqual(url, '/')
    
    def test_login_url(self):
        """
        Test login url in Circulation Desk
        """
        url = reverse('circulation_desk:login')
        self.assertEqual(url, '/login/')
    
    def test_login_nsec_url(self):
        """
        Test login-nsec url in Circulation Desk
        """
        url = reverse('circulation_desk:login-nsec')
        self.assertEqual(url, '/login-nsec/')
    
    def test_login_npub_url(self):
        """
        Test login-npub url in Circulation Desk
        """
        url = reverse('circulation_desk:login-npub')
        self.assertEqual(url, '/login-npub/')
    
    def test_logout_url(self):
        """
        Test logout url in Circulation Desk
        """
        url = reverse('circulation_desk:logout')
        self.assertEqual(url, '/logout/')
    
    def test_login_seed_url(self):
        """
        Test login-seed url in Circulation Desk
        """
        url = reverse('circulation_desk:login-seed')
        self.assertEqual(url, '/login-seed/')
    
    def test_create_account_url(self):
        """
        Test create-account url in Circulation Desk
        """
        url = reverse('circulation_desk:create-account')
        self.assertEqual(url, '/create-account/')
    
    def test_create_account_confirm_url(self):
        """
        Test create-account-confirm url in Circulation Desk
        """
        url = reverse('circulation_desk:create-account-confirm')
        self.assertEqual(url, '/create-account-confirm/')

    def tearDown(self):
        pass
