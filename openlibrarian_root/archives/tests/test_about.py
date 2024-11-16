from circulation_desk.tests.test_index import BaseFunctionalTest, BaseUnitTests
from selenium import webdriver
from selenium.webdriver.common.by import By


class AboutFunctionalTestCase(BaseFunctionalTest):
    """
    Functional Tests for the about page
    """
    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.url = "/archives/"
        self.driver = webdriver.Firefox()
        
    def test_home(self):
        """
        Test home button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="home").click()
        self.assertIn("/", self.driver.current_url)
    
    def test_login(self):
        """
        Test login button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="login").click()
        self.assertIn("/login/", self.driver.current_url)
    
    def test_signup(self):
        """
        Test signup button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="signup").click()
        self.assertIn("/create-account/", self.driver.current_url)

    def tearDown(self):
        """
        Tear Down function to close driver
        """
        self.driver.close()

class AboutUnitTestCase(BaseUnitTests):
    """
    Unit Tests for the about page
    """
    def setUp(self):
        self.url = "/archives/"
        self.template = "archives/about.html"
        self.content = ["Current Features", "Privacy", "Log-in", "Home", "Sign-up"]
        self.redirect = False