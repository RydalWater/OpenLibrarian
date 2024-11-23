from django.test import TestCase
from django.urls import reverse

# Unit tests for forms
class TestUrls(TestCase):
    """
    Unit tests for app urls
    """
    def setUp(self):
        pass
    
    def test_about_url(self):
        """
        Test about url in Archives
        """
        url = reverse('archives:about')
        self.assertEqual(url, '/archives/')
    
    def test_updates_url(self):
        """
        Test updates url in Archives
        """
        url = reverse('archives:updates')
        self.assertEqual(url, '/archives/updates/')
    
    def test_privacy_url(self):
        """
        Test privacy url in Archives
        """
        url = reverse('archives:privacy')
        self.assertEqual(url, '/archives/privacy/')
        
    def tearDown(self):
        pass
