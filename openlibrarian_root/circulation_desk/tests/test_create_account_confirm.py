from circulation_desk.tests.test_index import BaseFunctionalTest
from circulation_desk.forms import SeedForm
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.test import TestCase, Client
from mnemonic import Mnemonic
from nostr_sdk import Keys
import io, sys

TC_NPUB = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
TC_NSEC = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"

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
        self.redirect = True
    
    def test_back(self):
        """
        Test Back Button
        """
        self.driver.get("http://127.0.0.1:8000/create-account/")
        self.driver.find_element(by=By.ID, value="seed-gen").click()
        self.driver.find_element(by=By.ID, value="save-seed").click()
        self.driver.find_element(by=By.ID, value="back").click()
        self.assertIn("Circulation Desk", self.driver.page_source)
    
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
        session["tnsec"] = TC_NSEC
        session["tnpub"] = TC_NPUB
        session.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    # Test template is correct
    def test_page_template(self):
        """
        Check page templates (inc. base.html)
        """
        session = self.client.session
        session["tnsec"] = TC_NSEC
        session["tnpub"] = TC_NPUB
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
        session["tnsec"] = TC_NSEC
        session["tnpub"] = TC_NPUB
        session.save()
        response = self.client.get(self.url)
        for item in self.content:
            self.assertIn(item.encode(), response.content)
    
    def test_logged_redirect(self):
        """
        Test the redirect response when logged in
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
    
    def test_tnpub_redirect(self):
        """
        Test the redirect response when tnpub is None
        """
        session = self.client.session
        session["tnpub"] = None
        session.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
    
    def test_post_valid_form_invalid_mnemonic(self):
        """
        Post with valid form but invalid mnemonic
        """
        session = self.client.session
        session["tnsec"] = TC_NSEC
        session["tnpub"] = TC_NPUB
        session.save()
        form_data = {'word1': 'apple', 'word2': 'banana', 'word3': 'carrot', 'word4': 'date', 'word5': 'egg', 'word6': 'fish', 'word7': 'grape', 'word8': 'honey', 'word9': 'ice', 'word10': 'jelly', 'word11': 'kumquat', 'word12': 'lemon'}
        word_list = Mnemonic("english").wordlist 
        form = SeedForm(form_data)
        self.assertTrue(form.is_valid())
        # Check context values
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.context["tnpub"], TC_NPUB)
        self.assertEqual(response.context["private_key_confirmed"],"Invalid mnemonic")
        self.assertEqual(response.context["word_list"], word_list)
        self.assertEqual(response.status_code, 200)

    def test_post_invalid_form(self):
        """
        Post with invalid form
        """
        session = self.client.session
        session["tnsec"] = TC_NSEC
        session["tnpub"] = TC_NPUB
        session.save()
        form_data = {'word1': 'apple', 'word2': 'banana', 'word3': 'carrot', 'word4': 'date'}
        word_list = Mnemonic("english").wordlist 
        form = SeedForm(form_data)
        self.assertFalse(form.is_valid())
        # Check context values
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.context["tnpub"], TC_NPUB)
        self.assertEqual(response.context["private_key_confirmed"],None)
        self.assertEqual(response.context["word_list"], word_list)
        self.assertEqual(response.status_code, 200)
    
    def test_post_valid_mnemonic_fail_npub(self):
        """
        Post with valid mnemonic not matching npub
        """
        session = self.client.session
        keys = Keys.generate()
        session["tnsec"] = keys.secret_key().to_bech32()
        session["tnpub"] = keys.public_key().to_bech32()
        session.save()
        form_data = {'word1':'engine', 'word2':'survey', 'word3':'rich', 'word4':'year', 'word5':'woman', 'word6':'keen', 'word7':'thrive', 'word8':'clip', 'word9':'patrol', 'word10':'patrol', 'word11':'next', 'word12':'quantum'}
        form = SeedForm(form_data)
        self.assertTrue(form.is_valid())
        # Check context values
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.context["tnpub"], session["tnpub"])
        self.assertEqual(response.context["private_key_confirmed"],"Mnemonic does not match NPUB")
        self.assertEqual(response.status_code, 200)
    
    def test_post_success(self):
        """
        Post with valid mnemonic matching npub (success)
        """
        session = self.client.session
        session["tnsec"] = TC_NSEC
        session["tnpub"] = TC_NPUB
        session.save()
        form_data = {'word1':'engine', 'word2':'survey', 'word3':'rich', 'word4':'year', 'word5':'woman', 'word6':'keen', 'word7':'thrive', 'word8':'clip', 'word9':'patrol', 'word10':'patrol', 'word11':'next', 'word12':'quantum'}
        form = SeedForm(form_data)
        self.assertTrue(form.is_valid())
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        response = self.client.post(self.url, data=form_data)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        event_str = output.split("\n")[2]
        self.assertIn('["r","wss://nos.lol/"]', event_str)
        self.assertIn('["r","wss://relay.damus.io/"]', event_str)
        self.assertIn('["r","wss://nostr.mom/"]', event_str)
        self.assertIn('["r","wss://relay.primal.net/"]', event_str)
        self.assertIn('"content":""', event_str)
        self.assertIn('"kind":10002', event_str)
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        self.assertEqual(session["tnpub"], None)
        self.assertEqual(session["tnsec"], None)
        self.assertEqual(session["npub"], TC_NPUB)
        self.assertEqual(session["nsec"], TC_NSEC)
        self.assertIn("libraries", session.keys())
        self.assertIn("interests", session.keys())
        self.assertIn("relays", session.keys())
        