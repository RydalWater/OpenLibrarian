from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By

# Functional Test Cases (user action)
class BaseFunctionalTest(TestCase):
    """
    General Functional Tests
    """
    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.url = "/"
        self.driver = webdriver.Firefox()
    
    def test_click_archives(self):
        """
        Click on archives button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="about").click()
        self.assertIn("/archives/", self.driver.current_url)
    
    def tearDown(self):
        """
        Tear Down function to close driver
        """
        self.driver.close()

# Index specific functional tests
class IndexFunctionalTests(TestCase):
    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.driver = webdriver.Firefox()

    # Tests where not logged in
    def test_click_login(self):
        """
        Click on login button
        """
        self.driver.get("http://127.0.0.1:8000/")
        self.driver.find_element(by=By.ID, value="login").click()
        self.assertIn("/login/", self.driver.current_url)
    
    def test_click_signup(self):
        """
        Click on signup button
        """
        self.driver.get("http://127.0.0.1:8000/")
        self.driver.find_element(by=By.ID, value="signup").click()
        self.assertIn("/create-account/", self.driver.current_url)
    
    def tearDown(self):
        """
        Tear Down function to close driver
        """
        self.driver.close()

# Unit Test Cases (indivudal functions)
class BaseUnitTests(TestCase):
    """
    Base Unit Tests (includes index page by default)
    """
    def setUp(self):
        self.url = "/"
        self.template = "circulation_desk/index.html"
        self.content = ["Circulation Desk", "Sign-up", "Log-in"]
    
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
        self.assertTemplateUsed(response, "circulation_desk/base.html")

    # Test Page features.
    def test_page_has_content(self):
        """
        Check page for specific fields
        """
        response = self.client.get(self.url)
        for item in self.content:
            self.assertIn(item.encode(), response.content)
    

# Index specific unit tests
class IndexUnitTests(TestCase):
    
    def setUp(self):
        self.testpage = "Circulation Desk"
        self.url = "/"
        self.template = "circulation_desk/index.html"
        self.content = ["Circulation Desk", "Sign-up", "Log-in"]

    def test_logged_in_npub(self):
        """
        Check Logged in Buttons (NPUB)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session.save()
        response = self.client.get("/")
        self.assertIn(b"Read-Only Mode", response.content)
        self.assertIn(b'id="logout"', response.content)
        self.assertIn(b'id="home"', response.content)
        self.assertIn(b'id="settings"', response.content)
        self.assertIn(b'id="social"', response.content)
        self.assertIn(b'id="glossary"', response.content)
        self.assertIn(b'id="library"', response.content)
    
    def test_logged_in_nsec(self):
        """
        Check Logged in Buttons (NSEC)
        """
        session = self.client.session
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session.save()
        response = self.client.get("/")
        self.assertNotIn(b"Read-Only Mode", response.content)
        self.assertIn(b"Shareable Profile", response.content)
        self.assertIn(b'id="logout"', response.content)
        self.assertIn(b'id="home"', response.content)
        self.assertIn(b'id="settings"', response.content)
        self.assertIn(b'id="social"', response.content)
        self.assertIn(b'id="glossary"', response.content)
        self.assertIn(b'id="library"', response.content)
    
    def test_urls_of_links(self):
        """
        Check URLs of links on page
        """
        response = self.client.get("/")
        self.assertIn(b'href="https://github.com/RydalWater/OpenLibrarian/issues"', response.content)
        self.assertIn(b'href="https://nostr.com/"', response.content)
        self.assertIn(b'href="https://openlibrary.org"', response.content)

    