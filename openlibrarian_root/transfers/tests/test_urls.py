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
        Test index url in Transfers
        """
        url = reverse('transfers:transfers')
        self.assertEqual(url, '/transfers/')

    def tearDown(self):
        pass
