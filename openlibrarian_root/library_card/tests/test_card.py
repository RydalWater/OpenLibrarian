from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from circulation_desk.tests.test_index import TC_NPUB, TC_NSEC, TC_RELAYS, TC_LIBRARIES, TC_PROGRESS

class CardFunctionalTestCase(TestCase):
    """
    Functional Tests for the Library Card page
    """
    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.url = f"/card/{TC_NPUB}/"
        self.driver = webdriver.Firefox()

    def test_explore(self):
        """
        Test explore button (not logged in)
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        sleep(5)
        self.driver.find_element(by=By.ID, value="explore").click()
        sleep(5)
        self.assertNotIn(f"/card/{TC_NPUB}/", self.driver.current_url)
        self.assertIn("Read-Only Mode", self.driver.page_source)

    def test_new(self):
        """
        Test signup button (not logged in)
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        sleep(5)
        self.driver.find_element(by=By.ID, value="new").click()
        self.assertIn("/create-account/", self.driver.current_url)

    def test_home(self):
        """
        Test home button (when logged in)
        """
        self.driver.get(f"http://127.0.0.1:8000/login-nsec/")
        self.driver.find_element(by=By.ID, value="nsec").send_keys(TC_NSEC)
        self.driver.find_element(by=By.ID, value="login").click()
        sleep(5)
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        sleep(2)
        self.assertIn("Home", self.driver.page_source)
        self.assertIn("Share", self.driver.page_source)
        self.driver.find_element(by=By.ID, value="home").click()
        sleep(5)
        self.assertIn("/", self.driver.current_url)
        self.assertIn("Circulation Desk", self.driver.page_source)

    def tearDown(self):
        """
        Tear Down function to close driver
        """
        self.driver.close()

class CardUnitTests(TestCase):
    """
    Unit Tests for the Library Card page
    """
    def setUp(self):
        self.url = f"/card/{TC_NPUB}/"
        self.template = "library_card/card.html"
        self.content = ["Library Card", "Reading", "Interests"]
    
    # Test page returns a 200 response
    def test_page_returns_200(self):
        """
        Page returns a 200 response
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    # Test template is correct
    def test_page_template(self):
        """
        Check page templates (inc. base.html)
        """
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, self.template)
        self.assertTemplateUsed(response, "circulation_desk/base_minimal.html")

    # Test Page features.
    def test_page_has_content(self):
        """
        Check page for specific fields
        """
        response = self.client.get(self.url)
        for item in self.content:
            self.assertIn(item.encode(), response.content)
    
