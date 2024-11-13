from circulation_desk.tests.test_index import BaseFunctionalTest, BaseUnitTests
from selenium import webdriver
from selenium.webdriver.common.by import By
from utils.Login import check_npub, check_nsec, check_mnemonic


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
    
    def test_back(self):
        """
        Login with Back Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="back").click()
        self.assertIn("/", self.driver.current_url)
    
    def test_generate_keys(self):
        """
        Generate Keys Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="seed-gen").click()
        self.assertIn("/create-account/", self.driver.current_url)
        self.assertIn("DO NOT SHARE your NSEC or Seed Words with anyone.", self.driver.page_source)
        self.assertIn("I have saved my seed", self.driver.page_source)
        self.assertNotIn("These are the same as a password", self.driver.page_source)
        tnsec = self.driver.find_element(by=By.ID, value="tnsec").get_attribute("value")
        self.assertTrue(check_nsec(tnsec))
        tnpub = self.driver.find_element(by=By.ID, value="tnpub").get_attribute("value")
        self.assertTrue(check_npub(tnpub))
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
        self.driver.find_element(by=By.ID, value="seed-gen").click()
        tnsec2 = self.driver.find_element(by=By.ID, value="tnsec").get_attribute("value")
        self.assertNotEqual(tnsec1, tnsec2)

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
    
    def test_redirect_post(self):
        """
        Redirect to index on post request (where not signing up)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session.save()
        response = self.client.post(f"http://127.0.0.1:8000{self.url}", data={"test": "test"})
        self.assertRedirects(response, "/")
    
    def test_no_redirect_post(self):
        """
        Do not redirect to index on post request (where signing up)
        """
        response = self.client.post(f"http://127.0.0.1:8000{self.url}", data={"generate_seed": "Generate"})
        self.assertEqual(response.status_code, 200)
        response = self.client.post(f"http://127.0.0.1:8000{self.url}", data={"confirm_seed": "Confirm"})
        self.assertRedirects(response, "/create-account-confirm/")