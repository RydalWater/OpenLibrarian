from circulation_desk.tests.test_index import BaseFunctionalTest, BaseUnitTests
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.test import Client
from django.urls import reverse
from time import sleep
from circulation_desk.tests.test_index import TC_NPUB

class LogoutFunctionalTestCase(BaseFunctionalTest):
    """
    Functional Tests for the login page
    """
    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.url = "/logout/"
        self.driver = webdriver.Firefox()
        
    def test_back(self):
        """
        Back to Circulation Desk Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="back").click()
        self.assertIn("/", self.driver.current_url)
        
    def tearDown(self):
        """
        Tear Down function to close driver
        """
        self.driver.close()

class LogoutUnitTestCase(BaseUnitTests):
    """
    Unit Tests for the logout page
    """
    def setUp(self):
        self.url = "/logout/"
        self.template = "circulation_desk/logout.html"
        self.content = ["logged out", "Back to Circulation Desk"]
        self.redirect = False
        self.client = Client()

    def test_logout_after_login_npub(self):
        """
        Test Logout from Index after Login (NPUB)
        """
        # Open the page and enter a value in the form field
        response = self.client.get('/login-npub/')
        self.assertEqual(response.status_code, 200)

        # Submit the form
        response = self.client.post('/login-npub/', {'npub': TC_NPUB})
        self.assertEqual(response.status_code, 302)  # Assuming a redirect

        # Check the session value is correct
        self.assertEqual(self.client.session['npub'], TC_NPUB)

        # Logout
        response = self.client.get('/')
        response = self.client.get(reverse('circulation_desk:logout'))

        # Check the session data is removed
        self.assertNotIn('npub', self.client.session)
    
    def test_logout_after_login_rw(self):
        """
        Test Logout from Index after Login (NSEC)
        """
        # Create a test client
        client = Client()
        session = client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session.save()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(session['nsec'], 'Y')
        self.assertEqual(session['npub'], TC_NPUB)
    
        # Logout
        response = client.get('/')
        response = client.get(reverse('circulation_desk:logout'))
    
        # Check the session data is removed
        self.assertNotIn('nsec', client.session)
        self.assertNotIn('npub', client.session)
    
    def test_logout_post_request(self):
        """
        Test Logout from Index after Login (NSEC)
        """
        # Create a test client
        client = Client()
        session = client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session.save()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(session['nsec'], 'Y')
        self.assertEqual(session['npub'], TC_NPUB)
    
        # Logout
        response = client.get('/')
        response = client.post(reverse('circulation_desk:logout'),data={})
    
        # Check the session data is removed
        self.assertNotIn('nsec', client.session)
        self.assertNotIn('npub', client.session)

        # Check URL is index
        self.assertEqual(response.url, '/')