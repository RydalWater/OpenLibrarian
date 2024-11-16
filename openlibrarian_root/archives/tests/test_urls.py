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

    def tearDown(self):
        pass
