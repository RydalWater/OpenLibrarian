from circulation_desk.tests.test_index import BaseFunctionalTest, BaseUnitTests
from selenium import webdriver
from selenium.webdriver.common.by import By


class PrivacyFunctionalTestCase(BaseFunctionalTest):
    """
    Functional Tests for the privacy page
    """
    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.url = "/archives/privacy/"
        self.driver = webdriver.Firefox()
        
    def test_back(self):
        """
        Test back button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="back").click()
        self.assertIn("/archives/", self.driver.current_url)
    def tearDown(self):
        """
        Tear Down function to close driver
        """
        self.driver.close()

class PrivacyUnitTestCase(BaseUnitTests):
    """
    Unit Tests for the privacy page
    """
    def setUp(self):
        self.url = "/archives/privacy/"
        self.template = "archives/privacy.html"
        self.content = ["Privacy", "GitHub", "Back"]
        self.redirect = False