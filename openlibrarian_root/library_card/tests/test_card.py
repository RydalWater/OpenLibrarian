from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from hashlib import sha256


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

TC_NPUB = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
TC_NSEC = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
TC_RELAYS = {"wss://relay.damus.io": None}

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
        sleep(1)
        self.driver.find_element(by=By.ID, value="explore").click()
        self.assertNotIn(f"/card/{TC_NPUB}/", self.driver.current_url)
        self.assertIn("Read-Only Mode", self.driver.page_source)

    def test_new(self):
        """
        Test signup button (not logged in)
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        sleep(1)
        self.driver.find_element(by=By.ID, value="new").click()
        self.assertIn("/create-account/", self.driver.current_url)

    def test_home(self):
        """
        Test home button (when logged in)
        """
        self.driver.get(f"http://127.0.0.1:8000/login-nsec/")
        self.driver.find_element(by=By.ID, value="nsec").send_keys(TC_NSEC)
        self.driver.find_element(by=By.ID, value="login").click()
        sleep(10)
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        sleep(20)
        self.assertIn("Home", self.driver.page_source)
        self.assertIn("Share", self.driver.page_source)
        self.driver.find_element(by=By.ID, value="home").click()
        sleep(10)
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
