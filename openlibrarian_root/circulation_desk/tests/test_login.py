from circulation_desk.tests.test_index import BaseFunctionalTest, BaseUnitTests
from selenium import webdriver
from selenium.webdriver.common.by import By


class LoginFunctionalTestCase(BaseFunctionalTest):
    """
    Functional Tests for the login page
    """

    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.url = "/login/"
        self.driver = webdriver.Firefox()
        self.redirect = True

    def test_login_npub(self):
        """
        Login with NPUB Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="npub").click()
        self.assertIn("/login-npub/", self.driver.current_url)

    def test_login_nip07(self):
        """
        Login with NPUB Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="nip07").click()
        self.assertIn("/login-nip07/", self.driver.current_url)

    def test_login_nsec(self):
        """
        Login with NSEC Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="nsec").click()
        self.assertIn("/login-nsec/", self.driver.current_url)

    def test_login_seed(self):
        """
        Login with Seed Words Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="seed").click()
        self.assertIn("/login-seed/", self.driver.current_url)

    def test_back(self):
        """
        Test Back Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="back").click()
        self.assertIn("Circulation Desk", self.driver.page_source)

    def tearDown(self):
        """
        Tear Down function to close driver
        """
        self.driver.close()


class LoginUnitTestCase(BaseUnitTests):
    """
    Unit Tests for the login page
    """

    def setUp(self):
        self.url = "/login/"
        self.template = "circulation_desk/login.html"
        self.content = [
            "Log-in",
            "Public Key, NPUB (read-only)",
            "Browser Extension (read/write)",
            "rivate Key, NSEC (read/write)",
            "Seed Words (read/write)",
            "Back",
        ]
        self.redirect = True
