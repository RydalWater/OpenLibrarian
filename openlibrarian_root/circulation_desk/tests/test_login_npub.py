from circulation_desk.tests.test_index import BaseFunctionalTest, BaseUnitTests
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
    
    def test_redirect_npub(self):
        """
        Automatic redirect when logged in (NPUB)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session.save()
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.assertIn("/", self.driver.current_url)
    
    def test_redirect_nsec(self):
        """
        Automatic redirect when logged in (NSEC)
        """
        session = self.client.session
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session.save()
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.assertIn("/", self.driver.current_url)
    
    def test_invalid_npub(self):
        """
        Test Invalid NPUB value
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="npub").send_keys("npubmadeup123456blahblah")
        self.driver.find_element(by=By.ID, value="submit").click()
        self.assertIn("/login-npub/", self.driver.current_url)
        self.assertIn("Invalid NPUB", self.driver.page_source)
    
    def test_valid_npub(self):
        """
        Test Valid NPUB value
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="npub").send_keys("npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n")
        self.driver.find_element(by=By.ID, value="submit").click()
        self.assertIn("/", self.driver.current_url)
    
    def test_back(self):
        """
        Login with Back Button
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
        self.assertEqual(client.session['relays'], None)
        self.assertIn('nym', client.session)
        self.assertIn('profile', client.session)
        self.assertIn('libraries', client.session)
        self.assertIn('interests', client.session)