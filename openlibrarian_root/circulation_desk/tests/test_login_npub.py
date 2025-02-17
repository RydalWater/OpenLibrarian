from circulation_desk.tests.test_index import BaseFunctionalTest, BaseUnitTests
from circulation_desk.forms import NpubForm
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.test import Client

class LoginNpubFunctionalTestCase(BaseFunctionalTest):
    """
    Functional Tests for the login page
    """
    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.url = "/login-npub/"
        self.driver = webdriver.Firefox()
        self.redirect = True
    
    def test_invalid_npub(self):
        """
        Test Invalid NPUB value
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="npub").send_keys("npubmadeup123456blahblah")
        self.driver.find_element(by=By.ID, value="login").click()
        self.assertIn("/login-npub/", self.driver.current_url)
        self.assertIn("Invalid NPUB", self.driver.page_source)
    
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

class LoginNpubUnitTestCase(BaseUnitTests):
    """
    Unit Tests for the login page (NPUB)
    """
    def setUp(self):
        self.url = "/login-npub/"
        self.template = "circulation_desk/login_npub.html"
        self.content = ["Log-in", "NPUB (read-only)", "Back"]
        self.redirect = True
    
    def test_login_session_data(self):
        """
        Test Session Data after Login (NPUB)
        """
         # Create a test client and login with NPUB
        client = Client()
        response = client.get('/login-npub/')
        response = client.post('/login-npub/', {'npub': 'npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n'})

        # Check the session variables are correct
        self.assertEqual(client.session['npub'], 'npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n')
        self.assertNotIn('nsec', client.session)
        self.assertEqual(client.session['relays'], {'wss://relay.damus.io': None, 'wss://relay.primal.net': None, 'wss://nos.lol': None, 'wss://nostr.mom': None})
        self.assertIn('nym', client.session)
        self.assertIn('profile', client.session)
        self.assertIn('libraries', client.session)
        self.assertIn('interests', client.session)
    
    def test_post_form_invalid(self):
        """
        Test invalid form (empty)
        """
        # Check form returns false
        data = {'npub': 'npub1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890'}
        form = NpubForm(data)
        self.assertFalse(form.is_valid())

    def test_post_invalid_npub(self):
        # Test post request with invalid data
        client = Client()
        data = {'npub': 'npub1234'}
        response = client.post('/login-npub/', data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertEqual(response.context['noted'], 'false:Invalid NPUB.')
