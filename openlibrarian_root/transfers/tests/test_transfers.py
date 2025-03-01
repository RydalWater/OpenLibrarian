from circulation_desk.tests.test_index import BaseFunctionalTest, BaseUnitTests
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.test import Client, TestCase
from time import sleep

TNPUB = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"

class TransfersFunctionalTestCase(BaseFunctionalTest):
    """
    Functional Tests for the Transfers page
    """
    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.url = "/transfers/"
        self.driver = webdriver.Firefox()
    
    def test_redirect_not_logged_in(self):
        """
        Automatic redirect when not logged in
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.assertNotIn(self.url, self.driver.current_url)
        self.assertIn("Circulation Desk", self.driver.page_source)
    
    def test_transfer_social(self):
        """
        Transfer social list Button
        """
        self.driver.get(f"http://127.0.0.1:8000/login-npub/")
        self.driver.find_element(by=By.ID, value="npub").send_keys(TNPUB)
        self.driver.find_element(by=By.ID, value="login").click()
        sleep(5)
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="social").click()
        self.assertIn("/social-clone/", self.driver.current_url)
        
    def test_back(self):
        """
        Test Back Button
        """
        self.driver.get(f"http://127.0.0.1:8000/login-npub/")
        self.driver.find_element(by=By.ID, value="npub").send_keys(TNPUB)
        self.driver.find_element(by=By.ID, value="login").click()
        sleep(5)
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="back").click()
        self.assertIn("/almanac/", self.driver.current_url)

    def tearDown(self):
        """
        Tear Down function to close driver
        """
        self.driver.close()

class TransfersUnitTestCase(TestCase):
    """
    Unit Tests for the Transfers page
    """
    def setUp(self):
        self.url = "/transfers/"
        self.template = "transfers/transfers.html"
        self.content = ["Transfers", "Import Social Lists", "Import Profile", "Import Reading Lists", "Back"]

    def test_page_all_features(self):
        """
        Test page returns 200, has templates and contains expected content.
        """
        client = Client()
        response = client.get('/login-nsec/')
        data = {'hasNsec': 'Y', 'npubValue': TNPUB}
        response = client.post('/login-nsec/', data, content_type='application/json')
        response = client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)
        self.assertTemplateUsed(response, "circulation_desk/base.html")
        for item in self.content:
            self.assertIn(item.encode(), response.content)