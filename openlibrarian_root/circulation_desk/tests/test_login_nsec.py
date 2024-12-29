from circulation_desk.tests.test_index import BaseFunctionalTest, BaseUnitTests
from circulation_desk.forms import NsecForm
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.test import Client
from nostr_sdk import Keys

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
        self.driver.find_element(by=By.ID, value="submit").click()
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
        response = client.get('/login-nsec/')
        response = client.post('/login-nsec/', {'nsec': 'nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm'})

        # Check the session variables are correct
        self.assertEqual(client.session['npub'], 'npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n')
        self.assertEqual(client.session['nsec'], 'nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm')
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
        data = {'nsec': ''}
        form = NsecForm(data)
        self.assertFalse(form.is_valid())

        # Test post request with invalid data
        client = Client()
        response = client.post('/login-nsec/', data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
    
    def test_post_form_invalid_nsec(self):
        """
        Test invalid form (value)
        """
        # Check form returns true
        data={'nsec': 'nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm12345'}
        form = NsecForm(data)
        self.assertTrue(form.is_valid())

        # Check NSEC rasies exception
        with self.assertRaises(Exception):
            Keys.parse(data['nsec'])

        # Test post request with invalid data
        client = Client()
        response = client.post('/login-nsec/', data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('error_message', response.context)