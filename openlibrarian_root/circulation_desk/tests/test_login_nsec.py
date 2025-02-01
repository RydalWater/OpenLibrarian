from circulation_desk.tests.test_index import BaseFunctionalTest, BaseUnitTests
from circulation_desk.forms import NsecForm
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.test import Client
from django.urls import reverse
import json

TC_NPUB = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"

class LoginNsecFunctionalTestCase(BaseFunctionalTest):
    """
    Functional Tests for the login page
    """
    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.url = "/login-nsec/"
        self.driver = webdriver.Firefox()
        self.redirect = True
    
    def test_invalid_nsec(self):
        """
        Test Invalid NSEC value
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="nsec").send_keys("nsecmadeup123456blahblah")
        self.driver.find_element(by=By.ID, value="login").click()
        self.assertIn(self.url, self.driver.current_url)
        self.assertIn("Invalid NSEC", self.driver.page_source)
        
    def test_back(self):
        """
        Test Back Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="back").click()
        self.assertIn("/login/", self.driver.current_url)
    
    def tearDown(self):
        """
        Tear Down function to close driver
        """
        self.driver.close()

class LoginNsecUnitTestCase(BaseUnitTests):
    """
    Unit Tests for the login page (NSEC)
    """
    def setUp(self):
        self.url = "/login-nsec/"
        self.template = "circulation_desk/login_nsec.html"
        self.content = ["Log-in", "NSEC (read/write)", "Back"]
        self.redirect = True
    
    def test_login_session_data(self):
        """
        Test Session Data after Login (NSEC)
        """
        # Create a test client and login with NSEC
        client = Client()

        # Check the session variables are not populated
        self.assertNotIn('npub', client.session)
        self.assertNotIn('libraries', client.session)
        self.assertNotIn('progress', client.session)

        # Login with NSEC post
        response = client.get('/login-nsec/')
        data = {"npubValue": TC_NPUB, "hasNsec": "Y", "decryptedEvents": []}
        response = client.post('/login-nsec/', data, content_type='application/json')

        # Check the session variables are correct
        self.assertEqual(client.session['npub'], TC_NPUB)
        self.assertIn('libraries', client.session)
        self.assertIn('progress', client.session)
    
    def test_get_returns_form(self):
        # Test that a GET request returns a form
        client = Client()
        response = self.client.get('/login-nsec/')
        self.assertIsInstance(response.context['form'], NsecForm)

    def test_get_request(self):
        # Test that a GET request returns a redirect
        response = self.client.get(reverse('circulation_desk:fetch_events'))
        self.assertEqual(response.status_code, 302)

    def test_post_request_empty_data(self):
        # Test that a POST request with empty data raises an exception
        with self.assertRaises(Exception) as e:
            response = self.client.post(reverse('circulation_desk:fetch_events'), data=json.dumps({}), content_type='application/json')
        self.assertEqual(str(e.exception), "Missing npub")
    
    def test_post_request_badNpub_data(self):
        # Test that a POST request with empty data raises an exception
        with self.assertRaises(Exception) as e:
            response = self.client.post(reverse('circulation_desk:fetch_events'), data=json.dumps({"npubValue": "npub1234567"}), content_type='application/json')
        self.assertEqual(str(e.exception), "Invalid npub")

    def test_post_request_invalid_json(self):
        # Test that a POST request with invalid JSON data returns a 400 response
        response = self.client.post(reverse('circulation_desk:fetch_events'), data='invalid json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['raw_events'], [])

    def test_post_request_valid_data(self):
        # Test that a POST request with valid data returns a 200 response
        data = {'npubValue': TC_NPUB, 'hasNsec': 'Y', 'refresh': ''}
        response = self.client.post(reverse('circulation_desk:fetch_events'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_post_request_refresh_shelves(self):
        # Test that a POST request with refresh='shelves' returns a 200 response
        data = {'npubValue': TC_NPUB, 'hasNsec': 'Y', 'refresh': 'shelves'}
        response = self.client.post(reverse('circulation_desk:fetch_events'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_post_request_refresh_invalid(self):
        # Test that a POST request with refresh='invalid' returns a 200 response with an empty list
        data = {'npubValue': TC_NPUB, 'hasNsec': 'Y', 'refresh': 'invalid'}
        response = self.client.post(reverse('circulation_desk:fetch_events'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['raw_events'], [])
    
    def test_post_request_invalid_credentials(self):
        # Test that a POST request with invalid credentials returns an error message
        data = {'npubValue': TC_NPUB, 'hasNsec': 'N', 'decryptedEvents': 'invalid data'}
        response = self.client.post(reverse('circulation_desk:login-nsec'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.json()['error_message'], 'Invalid Credentials')