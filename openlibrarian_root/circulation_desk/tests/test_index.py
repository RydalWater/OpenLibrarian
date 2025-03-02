from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from hashlib import sha256

TC_NPUB = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
TC_NSEC = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
TC_RELAYS = {"wss://relay.damus.io": None, "wss://nostr.mom": "READ"}
TC_LIBRARIES = [
    {'s': 'TRS', 'i': 'aea571dbde5eb6ebec93c91b95486539b9491962', 't': 'To Read (S)', 'd': 'Books on the shelf ready to read', 'c': 'Books & Literature (OpenLibrarian)', 'b': [{'t': 'The Olive Farm', 'a': 'Carol Drinkwater', 'i': '0349114749', 'c': 'https://covers.openlibrary.org/b/isbn/0349114749-M.jpg', 'h': 'N'}, {'t': 'Beauty', 'a': 'Sheri S. Tepper', 'i': '1857987225', 'c': 'https://covers.openlibrary.org/b/isbn/1857987225-M.jpg', 'h': 'N'}, {'t': 'Angry Aztecs', 'a': 'Terry Deary', 'i': '9781407104256', 'c': 'https://covers.openlibrary.org/b/isbn/9781407104256-M.jpg', 'h': 'N'}, {'t': 'March', 'a': 'Geraldine Brooks', 'i': '0007165870', 'c': 'https://covers.openlibrary.org/b/isbn/0007165870-M.jpg', 'h': 'N'}]},
    {'s': 'TRW', 'i': 'f76a2d0c13b20a32eeefc4e4f5b393f7b0d6dccc', 't': 'To Read (W)', 'd': "Books I want to read but do not own yet", 'c': 'Books & Literature (OpenLibrarian)', 'b': [{'t': 'Tomorrow', 'a': 'Unknown Author', 'i': '9780718183899', 'c': 'https://covers.openlibrary.org/b/isbn/9780718183899-M.jpg', 'h': 'Y'}, {'t': 'Flesh House', 'a': 'Stuart MacBride', 'i': '9780007244546', 'c': 'https://covers.openlibrary.org/b/isbn/9780007244546-M.jpg', 'h': 'Y'}]},
    {'s': 'CR', 'i': 'fe7046323fc3ccc7c6b2748ba58295fc4206a1a3', 't': 'Currently Reading', 'd': 'Books I am currently reading', 'c': 'Books & Literature (OpenLibrarian)', 'b': [{'t': 'MANDIBLES A FAMILY 2029-47_PB', 'a': 'SHRIVER  LIONEL', 'i': '9780007560776', 'c': 'https://covers.openlibrary.org/b/isbn/9780007560776-M.jpg', 'h': 'N'}]},
    {'s': 'HR', 'i': 'e1d342f8901e9db6dcd671b974e130f8bc5353f7', 't': 'Have Read', 'd': 'Books I have finished reading', 'c': 'Books & Literature (OpenLibrarian)', 'b': [{'t': "Walker's Guide to Outdoor Clues and Signs", 'a': 'Tristan Gooley', 'i': '9781444780109', 'c': 'https://covers.openlibrary.org/b/isbn/9781444780109-M.jpg', 'h': 'Y'}, {'t': 'Humankind', 'a': 'Rutger Bregman', 'i': '9781408898956', 'c': 'https://covers.openlibrary.org/b/isbn/9781408898956-M.jpg', 'h': 'Y'}, {'t': 'Hackers', 'a': 'Steven Levy', 'i': '0140232699', 'c': 'https://covers.openlibrary.org/b/isbn/0140232699-M.jpg', 'h': 'Y'}]}
]
TC_PROGRESS = {
    "9780007560776" : {
    "id": sha256("9780007560776".encode()).hexdigest(),
    "exid": "isbn",
    "unit": "pct","curr": "0",
    "max": "100",
    "st": "NA",
    "en": "NA",
    "default": "NOT AVAILABLE",
    "progress": "0"},
    "9781444780109" : {
    "id": sha256("9781444780109".encode()).hexdigest(),
    "exid": "isbn",
    "unit": "pct",
    "curr": "100",
    "max": "100",
    "st": "NA",
    "en": "NA",
    "default": "NOT AVAILABLE",
    "progress": "0"},
    "9781408898956" : {
    "id": sha256("9781408898956".encode()).hexdigest(),
    "exid": "isbn",
    "unit": "pct",
    "curr": "100",
    "max": "100",
    "st": "NA",
    "en": "NA",
    "default": "NOT AVAILABLE",
    "progress": "0"},
    "0140232699" : {
    "id": sha256("0140232699".encode()).hexdigest(),
    "exid": "isbn",
    "unit": "pct",
    "curr": "100",
    "max": "100",
    "st": "NA",
    "en": "NA",
    "default": "NOT AVAILABLE",
    "progress": "0"}
}
TC_ISBNS = ["9781444780109","9781408898956","0140232699","9780007560776"]
TC_REVIEWS = {
    "9781444780109": {"id": "a479b971d0d1e054dae477e8eed7a4897ef62e86de547de73c98ca6b05261783", "exid": "isbn", "rating": 4.5, "content": "Love it!", "tags": [], "rating_normal": "0.9", "rating_raw": "4.5/5"},
}

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
    