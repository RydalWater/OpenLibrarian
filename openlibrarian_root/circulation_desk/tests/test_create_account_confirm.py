from circulation_desk.tests.test_index import BaseFunctionalTest, BaseUnitTests
from selenium import webdriver
from selenium.webdriver.common.by import By
from utils.Login import check_npub, check_nsec, check_mnemonic
from django.test import TestCase, Client


class CreateAccountConfirmFunctionalTestCase(BaseFunctionalTest):
    """
    Functional Tests for the create account page
    """
    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.url = "/create-account-confirm/"
        self.driver = webdriver.Firefox()
    
    def test_redirect_npub(self):
        """
        Automatic redirect when logged in (NPUB)
        """
        self.driver.get(f"http://127.0.0.1:8000/login-npub/")
        self.driver.find_element(by=By.ID, value="npub").send_keys("npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n")
        self.driver.find_element(by=By.ID, value="submit").click()
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.assertNotIn(self.url, self.driver.current_url)
        self.assertIn("Circulation Desk", self.driver.page_source)
    
    def test_redirect_nsec(self):
        """
        Automatic redirect when logged in (NSEC)
        """
        self.driver.get(f"http://127.0.0.1:8000/login-nsec/")
        self.driver.find_element(by=By.ID, value="nsec").send_keys("nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm")
        self.driver.find_element(by=By.ID, value="submit").click()
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.assertNotIn(self.url, self.driver.current_url)
        self.assertIn("Circulation Desk", self.driver.page_source)
    
    def test_back(self):
        """
        Login with Back Button
        """
        self.driver.get("http://127.0.0.1:8000/create-account/")
        self.driver.find_element(by=By.ID, value="seed-gen").click()
        self.driver.find_element(by=By.ID, value="save-seed").click()
        self.driver.find_element(by=By.ID, value="back").click()
        self.assertIn("/", self.driver.current_url)
    
    def test_correct_seed(self):
        """
        Signup with correct seed
        """
        self.driver.get("http://127.0.0.1:8000/create-account/")
        self.driver.find_element(by=By.ID, value="seed-gen").click()
        twords = []
        for i in range(12):
            twords.append(self.driver.find_element(by=By.ID, value=f"tword{i+1}").get_attribute("value"))
        self.driver.find_element(by=By.ID, value="save-seed").click()
        for i in range(12):
            self.driver.find_element(by=By.ID, value=f"word{i+1}").send_keys(twords[i])
        self.driver.find_element(by=By.ID, value="submit").click()
        self.assertIn("Success! Your account has been created.", self.driver.page_source)

    def test_incorrect_seed(self):
        """
        Signup with incorrect seed
        """
        self.driver.get("http://127.0.0.1:8000/create-account/")
        self.driver.find_element(by=By.ID, value="seed-gen").click()
        twords = ["apple", "banana", "cherry", "date", "egg", "fig", "grape", "honey", "ice", "juice", "kiwi", "lemon"]
        self.driver.find_element(by=By.ID, value="save-seed").click()
        for i in range(12):
            self.driver.find_element(by=By.ID, value=f"word{i+1}").send_keys(twords[i])
        self.driver.find_element(by=By.ID, value="submit").click()
        self.assertIn("Invalid mnemonic", self.driver.page_source)   
        self.assertIn(self.url, self.driver.current_url)       
            
    def tearDown(self):
        """
        Tear Down function to close driver
        """
        self.driver.close()

class CreateAccountConfirmUnitTestCase(TestCase):
    """
    Unit Tests for the Create Account page
    """
    def setUp(self):
        self.client = Client()
        self.url = "/create-account-confirm/"
        self.template = "circulation_desk/create_account_confirm.html"
        self.content = ["Sign-up", "NPUB", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "Check", "Back"]

    def test_page_returns_200(self):
        """
        Page returns a 200 response
        """
        session = self.client.session
        session["tnsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session["tnpub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    # Test template is correct
    def test_page_template(self):
        """
        Check page templates (inc. base.html)
        """
        session = self.client.session
        session["tnsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session["tnpub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session.save()
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, self.template)
        self.assertTemplateUsed(response, "circulation_desk/base.html")

    # Test Page features.
    def test_page_has_content(self):
        """
        Check page for specific fields
        """
        session = self.client.session
        session["tnsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session["tnpub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session.save()
        response = self.client.get(self.url)
        for item in self.content:
            self.assertIn(item.encode(), response.content)