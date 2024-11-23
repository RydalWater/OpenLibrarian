from django.test import TestCase
from django.urls import reverse

# Unit tests for forms
class TestUrls(TestCase):
    """
    Unit tests for app urls
    """
    def setUp(self):
        pass
    
    def test_settings_url(self):
        """
        Test settings url in Almanac
        """
        url = reverse('almanac:settings')
        self.assertEqual(url, '/almanac/')
    
    def test_profile_url(self):
        """
        Test profile url in Almanac
        """
        url = reverse('almanac:user_profile')
        self.assertEqual(url, '/almanac/profile/')
    
    def test_relays_url(self):
        """
        Test relays url in Almanac
        """
        url = reverse('almanac:user_relays')
        self.assertEqual(url, '/almanac/relays/')
    
    def test_friends_url(self):
        """
        Test friends url in Almanac
        """
        url = reverse('almanac:user_friends')
        self.assertEqual(url, '/almanac/friends/')
        
    def tearDown(self):
        pass
