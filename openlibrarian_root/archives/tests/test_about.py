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
        
    def test_back(self):
        """
        Test back button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="back").click()
        self.assertIn("/", self.driver.current_url)
    
    def test_update(self):
        """
        Test updates button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="updates").click()
        self.assertIn("/archives/updates/", self.driver.current_url)
    
    def test_privacy(self):
        """
        Test privacy button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="privacy").click()
        self.assertIn("/archives/privacy/", self.driver.current_url)

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
        self.content = ["About", "Updates & Features", "Privacy Policy", "Back"]
        self.redirect = False