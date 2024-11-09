from .test_index import BaseFunctionalTest, BaseUnitTests
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
    
    def test_redirect_npub(self):
        """
        Automatic redirect when logged in (NPUB)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session.save()
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.assertIn("/", self.driver.current_url)
    
    def test_redirect_nsec(self):
        """
        Automatic redirect when logged in (NSEC)
        """
        session = self.client.session
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session.save()
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.assertIn("/", self.driver.current_url)
    
    def test_login_npub(self):
        """
        Login with NPUB Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="npub").click()
        self.assertIn("/login-npub/", self.driver.current_url)

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
        Login with Back Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="back").click()
        self.assertIn("/", self.driver.current_url)

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
        self.content = ["Log-in", "NPUB (read-only)", "NSEC (read/write)", "Seed Words (read/write)", "Back"]