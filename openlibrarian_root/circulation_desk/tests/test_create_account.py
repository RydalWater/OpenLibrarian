from circulation_desk.tests.test_index import BaseFunctionalTest, BaseUnitTests
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.test import Client
from utils.Login import check_npub, check_nsec, check_mnemonic, check_npub_of_nsec
from time import sleep

class CreateAccountFunctionalTestCase(BaseFunctionalTest):
    """
    Functional Tests for the create account page
    """
    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.url = "/create-account/"
        self.driver = webdriver.Firefox()
        self.redirect = True
    
    def test_back(self):
        """
        Test Back Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="back").click()
        self.assertIn("Circulation Desk", self.driver.page_source)
    
    def test_generate_keys(self):
        """
        Generate Keys Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="seed-gen").click()
        sleep(1)
        self.assertIn("/create-account/", self.driver.current_url)
        tnsec = self.driver.find_element(by=By.ID, value="tnsec").get_attribute("value")
        self.assertTrue(check_nsec(tnsec))
        tnpub = self.driver.find_element(by=By.ID, value="tnpub").get_attribute("value")
        self.assertTrue(check_npub(tnpub))
        self.assertTrue(check_npub_of_nsec(tnpub, tnsec))
        tseed = ""
        for i in range(12):
            tword = self.driver.find_element(by=By.ID, value=f"tword{i+1}").get_attribute("value")
            tseed += tword + " "
        self.assertTrue(check_mnemonic(tseed.rstrip()))
    
    def test_repeat_generate_keys(self):
        """
        Repeat Generate Keys Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="seed-gen").click()
        tnsec1 = self.driver.find_element(by=By.ID, value="tnsec").get_attribute("value")
        tnpub1 = self.driver.find_element(by=By.ID, value="tnpub").get_attribute("value")

        self.driver.find_element(by=By.ID, value="seed-gen").click()
        tnsec2 = self.driver.find_element(by=By.ID, value="tnsec").get_attribute("value")
        tnpub2 = self.driver.find_element(by=By.ID, value="tnpub").get_attribute("value")
        
        self.assertNotEqual(tnsec1, tnsec2)
        self.assertNotEqual(tnpub1, tnpub2)

    def test_saved_seed(self):
        """
        Save Seed Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="seed-gen").click()
        tnpub1 = self.driver.find_element(by=By.ID, value="tnpub").get_attribute("value")
        self.driver.find_element(by=By.ID, value="save-seed").click()
        self.assertIn("/create-account-confirm/", self.driver.current_url)
        tnpub2 = self.driver.find_element(by=By.ID, value="tnpub").get_attribute("value")
        self.assertEqual(tnpub1, tnpub2)
        
    def tearDown(self):
        """
        Tear Down function to close driver
        """
        self.driver.close()

class CreateAccountUnitTestCase(BaseUnitTests):
    """
    Unit Tests for the Create Account page
    """
    def setUp(self):
        self.url = "/create-account/"
        self.template = "circulation_desk/create_account.html"
        self.content = ["Sign-up", "Secret Key", "Public Key", "Generate Keys", "Back"]
        self.redirect = True
        self.client = Client()
    
    def test_context(self):
        """
        Test that the correct context is passed to the template
        """
        response = self.client.get(self.url)
        self.context = response.context
        self.assertIn("num_words", self.context.keys())
        self.assertEqual(self.context["num_words"], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])