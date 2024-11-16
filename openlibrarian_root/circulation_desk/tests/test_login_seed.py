from circulation_desk.tests.test_index import BaseFunctionalTest, BaseUnitTests
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.test import Client


class LoginSeedFunctionalTestCase(BaseFunctionalTest):
    """
    Functional Tests for the login page
    """
    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.url = "/login-seed/"
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
    
    def test_invalid_seed(self):
        """
        Test Invalid Seed Words
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="word1").send_keys("apple")
        self.driver.find_element(by=By.ID, value="word2").send_keys("banana")
        self.driver.find_element(by=By.ID, value="word3").send_keys("cherry")
        self.driver.find_element(by=By.ID, value="word4").send_keys("date")
        self.driver.find_element(by=By.ID, value="word5").send_keys("egg")
        self.driver.find_element(by=By.ID, value="word6").send_keys("fig")
        self.driver.find_element(by=By.ID, value="word7").send_keys("grape")
        self.driver.find_element(by=By.ID, value="word8").send_keys("honey")
        self.driver.find_element(by=By.ID, value="word9").send_keys("ice")
        self.driver.find_element(by=By.ID, value="word10").send_keys("juice")
        self.driver.find_element(by=By.ID, value="word11").send_keys("kiwi")
        self.driver.find_element(by=By.ID, value="word12").send_keys("lemon")
        self.driver.find_element(by=By.ID, value="submit").click()
        self.assertIn("/login-seed/", self.driver.current_url)
        self.assertIn("Invalid Seed", self.driver.page_source)
    
    def test_valid_npub(self):
        """
        Test Valid Seed Words
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="word1").send_keys("engine")
        self.driver.find_element(by=By.ID, value="word2").send_keys("survey")
        self.driver.find_element(by=By.ID, value="word3").send_keys("rich")
        self.driver.find_element(by=By.ID, value="word4").send_keys("year")
        self.driver.find_element(by=By.ID, value="word5").send_keys("woman")
        self.driver.find_element(by=By.ID, value="word6").send_keys("keen")
        self.driver.find_element(by=By.ID, value="word7").send_keys("thrive")
        self.driver.find_element(by=By.ID, value="word8").send_keys("clip")
        self.driver.find_element(by=By.ID, value="word9").send_keys("patrol")
        self.driver.find_element(by=By.ID, value="word10").send_keys("patrol")
        self.driver.find_element(by=By.ID, value="word11").send_keys("next")
        self.driver.find_element(by=By.ID, value="word12").send_keys("quantum")
        self.driver.find_element(by=By.ID, value="submit").click()
        self.assertNotIn("/login-seed/", self.driver.current_url)
    
    def test_back(self):
        """
        Login with Back Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="back").click()
        self.assertIn("/login/", self.driver.current_url)
    
    def tearDown(self):
        """
        Tear Down function to close driver
        """
        self.driver.close()

class LoginSeedUnitTestCase(BaseUnitTests):
    """
    Unit Tests for the login page (Seed)
    """
    def setUp(self):
        self.url = "/login-seed/"
        self.template = "circulation_desk/login_seed.html"
        self.content = ["Log-in", "Seed Words (read/write)", "Back"]
    
    def test_login_session_data(self):
        """
        Test Session Data after Login (Seed)
        """
         # Create a test client and login with NSEC
        client = Client()
        response = client.get('/login-seed/')
        response = client.post('/login-seed/', {'word1': 'engine', 'word2': 'survey', 'word3': 'rich', 'word4': 'year', 'word5': 'woman', 'word6': 'keen', 'word7': 'thrive', 'word8': 'clip', 'word9': 'patrol', 'word10': 'patrol', 'word11': 'next', 'word12': 'quantum'})

        # Check the session variables are correct
        self.assertEqual(client.session['npub'], 'npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n')
        self.assertEqual(client.session['nsec'], 'nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm')
        self.assertEqual(client.session['relays'], None)
        self.assertIn('nym', client.session)
        self.assertIn('profile', client.session)
        self.assertIn('libraries', client.session)
        self.assertIn('interests', client.session)