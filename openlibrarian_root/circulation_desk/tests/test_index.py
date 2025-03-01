from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

TC_NPUB = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"

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
        BASE: Click on archives button
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
    
    def test_click_almanac(self):
        """
        Click on Almanac button (logged in)
        """
        self.driver.get("http://127.0.0.1:8000/login-npub/")
        self.driver.find_element(by=By.ID, value="npub").send_keys(TC_NPUB)
        self.driver.find_element(by=By.ID, value="login").click()
        sleep(3)
        self.driver.get("http://127.0.0.1:8000/")
        self.driver.find_element(by=By.ID, value="almanac").click()
        self.assertIn("/almanac/", self.driver.current_url)
    
    def test_click_catalogue(self):
        """
        Click on Catalogue button (logged in)
        """
        self.driver.get("http://127.0.0.1:8000/login-npub/")
        self.driver.find_element(by=By.ID, value="npub").send_keys(TC_NPUB)
        self.driver.find_element(by=By.ID, value="login").click()
        sleep(3)
        self.driver.get("http://127.0.0.1:8000/")
        self.driver.find_element(by=By.ID, value="catalogue").click()
        self.assertIn("/catalogue/", self.driver.current_url)
    
    def test_click_library(self):
        """
        Click on Library button (logged in)
        """
        self.driver.get("http://127.0.0.1:8000/login-npub/")
        self.driver.find_element(by=By.ID, value="npub").send_keys(TC_NPUB)
        self.driver.find_element(by=By.ID, value="login").click()
        sleep(3)
        self.driver.get("http://127.0.0.1:8000/")
        self.driver.find_element(by=By.ID, value="library").click()
        self.assertIn("/library/", self.driver.current_url)
    
    def test_click_logout(self):
        """
        Click on logout button (logged in)
        """
        self.driver.get("http://127.0.0.1:8000/login-npub/")
        self.driver.find_element(by=By.ID, value="npub").send_keys(TC_NPUB)
        self.driver.find_element(by=By.ID, value="login").click()
        sleep(3)
        self.driver.get("http://127.0.0.1:8000/")
        self.driver.find_element(by=By.ID, value="logout").click()
        self.assertIn("/logout/", self.driver.current_url)
    
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
        self.content = ["Circulation Desk", "Sign-up", "Log-in","an open social network protocol","heart of this app is built on the brilliant work"]
        self.redirect = False
    
    # Test page returns a 200 response
    def test_page_returns_200(self):
        """
        BASE: Page returns a 200 response
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    # Test template is correct
    def test_page_template(self):
        """
        BASE: Check page templates (inc. base.html)
        """
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, self.template)
        self.assertTemplateUsed(response, "circulation_desk/base.html")

    # Test Page features.
    def test_page_has_content(self):
        """
        BASE: Check page for specific fields
        """
        response = self.client.get(self.url)
        for item in self.content:
            self.assertIn(item.encode(), response.content)

    # Test redirect when logged
    def test_logged_redirect(self):
        """
        BASE: Test the redirect response when logged in
        """
        if self.redirect:
            session = self.client.session
            session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
            session.save()
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, "/")
        else:
            self.skipTest("Redirect not expected")
    

# Index specific unit tests
class IndexUnitTests(TestCase):
    
    def setUp(self):
        self.testpage = "Circulation Desk"
        self.url = "/"
        self.template = "circulation_desk/index.html"
        self.content = ["Circulation Desk", "Sign-up", "Log-in"]
        self.redirect = False

    def test_logged_in_npub(self):
        """
        Check Logged in Buttons (NPUB)
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session.save()
        response = self.client.get("/")
        self.assertIn(b"Read-Only Mode", response.content)
        self.assertIn(b"Shareable Profile", response.content)
        self.assertIn(b'id="logout"', response.content)
        self.assertIn(b'id="home"', response.content)
        self.assertIn(b'id="settings"', response.content)
        self.assertIn(b'id="social"', response.content)
        self.assertIn(b'id="catalogue"', response.content)
        self.assertIn(b'id="library"', response.content)
        self.assertIn(b'Almanac (Settings)', response.content)
        self.assertIn(b'Catalogue (Search)', response.content)
        self.assertIn(b'Library (My Books)', response.content)
        self.assertIn(b'Logout', response.content)
        self.assertNotIn(b"Sign-up", response.content)
        self.assertNotIn(b"Log-in", response.content)
        self.assertNotIn(b"an open social network protocol", response.content)
        self.assertNotIn(b"heart of this app is built on the brilliant work", response.content)

    
    def test_logged_in_nsec(self):
        """
        Check Logged in Buttons (NSEC)
        """
        session = self.client.session
        session["nsec"] = "Y"
        session["npub"] = TC_NPUB
        session.save()
        response = self.client.get("/")
        self.assertNotIn(b"Read-Only Mode", response.content)
        self.assertIn(b"My Shareable Profile", response.content)
        self.assertIn(b'id="logout"', response.content)
        self.assertIn(b'id="home"', response.content)
        self.assertIn(b'id="settings"', response.content)
        self.assertIn(b'id="social"', response.content)
        self.assertIn(b'id="catalogue"', response.content)
        self.assertIn(b'id="library"', response.content)
        self.assertIn(b'Almanac (Settings)', response.content)
        self.assertIn(b'Catalogue (Search)', response.content)
        self.assertIn(b'Library (My Books)', response.content)
        self.assertIn(b'Logout', response.content)
        self.assertNotIn(b"Sign-up", response.content)
        self.assertNotIn(b"Log-in", response.content)
        self.assertNotIn(b"an open social network protocol", response.content)
        self.assertNotIn(b"heart of this app is built on the brilliant work", response.content)

    def test_urls_of_links(self):
        """
        Check URLs of links on page
        """
        response = self.client.get("/")
        self.assertIn(b'href="https://github.com/RydalWater/OpenLibrarian/issues"', response.content)
        self.assertIn(b'href="https://nostr.com/"', response.content)
        self.assertIn(b'href="https://openlibrary.org"', response.content)
    