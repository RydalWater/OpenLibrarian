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
        self.url = "/login-nip07/"
        self.driver = webdriver.Firefox()
        self.redirect = True
    
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
        self.url = "/login-nip07/"
        self.template = "circulation_desk/login_nip07.html"
        self.content = ["Log-in", "Browser Extension, NIP-07 (read/write)", "Back"]
        self.redirect = True