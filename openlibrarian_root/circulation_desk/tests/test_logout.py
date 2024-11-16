from circulation_desk.tests.test_index import BaseFunctionalTest, BaseUnitTests
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.test import Client
from django.urls import reverse

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

    def test_logout_after_login_npub(self):
        """
        Test Logout from Index after Login (NPUB)
        """
         # Create a test client
        client = Client()

        # Open the page and enter a value in the form field
        response = client.get('/login-npub/')
        self.assertEqual(response.status_code, 200)

        # Submit the form
        response = client.post('/login-npub/', {'npub': 'npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n'})
        self.assertEqual(response.status_code, 302)  # Assuming a redirect

        # Check the session value is correct
        self.assertEqual(client.session['npub'], 'npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n')

        # Logout
        response = client.get('/')
        response = client.get(reverse('circulation_desk:logout'))

        # Check the session data is removed
        self.assertNotIn('npub', client.session)
    
    def test_logout_after_login_nsec(self):
        """
        Test Logout from Index after Login (NSEC)
        """
        # Create a test client
        client = Client()

        # Open the page and enter a value in the form field
        response = client.get('/login-nsec/')
        self.assertEqual(response.status_code, 200)

        # Submit the form
        response = client.post('/login-nsec/', {'nsec': 'nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm'})
        self.assertEqual(response.status_code, 302)  # Assuming a redirect

        # Check the session value is correct
        self.assertEqual(client.session['nsec'], 'nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm')
        self.assertEqual(client.session['npub'], 'npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n')

        # Logout
        response = client.get('/')
        response = client.get(reverse('circulation_desk:logout'))

        # Check the session data is removed
        self.assertNotIn('nsec', client.session)
        self.assertNotIn('npub', client.session)
    
    def test_logout_after_login_seed(self):
        """
        Test Logout from Index after Login (SEED)
        """
        # Create a test client
        client = Client()

        # Open the page and enter a value in the form field
        response = client.get('/login-seed/')
        self.assertEqual(response.status_code, 200)

        # Submit the form
        response = client.post('/login-seed/', {'word1': 'engine', 'word2': 'survey', 'word3': 'rich', 'word4': 'year', 'word5': 'woman', 'word6': 'keen', 'word7': 'thrive', 'word8': 'clip', 'word9': 'patrol', 'word10': 'patrol', 'word11': 'next', 'word12': 'quantum'})
        self.assertEqual(response.status_code, 302)  # Assuming a redirect

        # Check the session value is correct
        self.assertEqual(client.session['nsec'], 'nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm')
        self.assertEqual(client.session['npub'], 'npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n')

        # Logout
        response = client.get('/')
        response = client.get(reverse('circulation_desk:logout'))

        # Check the session data is removed
        self.assertNotIn('nsec', client.session)
        self.assertNotIn('npub', client.session)