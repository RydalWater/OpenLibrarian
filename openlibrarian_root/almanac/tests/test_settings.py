from django.test import TestCase, Client
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

TC_NPUB = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
TC_NSEC = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"

class SettingsFunctionalTestCase(TestCase):
    """
    Functional Tests for the settings page
    """
    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.url = "/almanac/"
        self.driver = webdriver.Firefox()
        self.driver.get(f"http://127.0.0.1:8000/login-npub/")
        self.driver.find_element(by=By.ID, value="npub").send_keys(TC_NPUB)
        self.driver.find_element(by=By.ID, value="submit").click()
        sleep(1)

    def test_almanac_profile(self):
        """
        Test Almanac Profile Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        sleep(1)
        self.driver.find_element(by=By.ID, value="profile").click()
        self.assertIn("/profile/", self.driver.current_url)
    
    def test_almanac_relays(self):
        """
        Test Almanac Relays Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        sleep(1)
        self.driver.find_element(by=By.ID, value="relays").click()
        self.assertIn("/relays/", self.driver.current_url)
    
    def test_almanac_friends(self):
        """
        Test Almanac Friends Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        sleep(1)
        self.driver.find_element(by=By.ID, value="friends").click()
        self.assertIn("/friends/", self.driver.current_url)
    
    def test_almanac_export_import(self):
        """
        Test Almanac Export/Import Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        sleep(1)
        self.driver.find_element(by=By.ID, value="transfers").click()
        self.assertIn("/transfers/", self.driver.current_url)

    def tearDown(self):
        """
        Tear Down function to close driver
        """
        self.driver.close()

class SettingsUnitTestCase(TestCase):
    """
    Unit Tests for the settings page
    """
    def setUp(self):
        self.url = "/almanac/"
        self.template = "almanac/user_setting.html"
        self.content = ["Almanac", "Profile", "Relays", "Friends", "Export/Import", "Advanced"]
        self.client = Client()
        self.readonly = False

    
    # Test page returns a 200 response
    def test_page_returns_200(self):
        """
        Page returns a 200 response when logged in
        """

        # Set session with login both NPUB and NSEC
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = TC_NSEC
        session.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        # Clear session and test login with just NPUB
        session.clear()
        session.save()
        self.assertNotIn("npub", session)
        self.assertNotIn("nsec", session)
        session["npub"] = TC_NPUB
        session.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    # Test template is correct
    def test_page_template(self):
        """
        Check page templates (inc. base.html) when logged in
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = TC_NSEC
        session.save()
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, self.template)
        self.assertTemplateUsed(response, "circulation_desk/base.html")

        # Clear session and test login with just NPUB
        session.clear()
        session.save()
        self.assertNotIn("npub", session)
        self.assertNotIn("nsec", session)
        session["npub"] = TC_NPUB
        session.save()
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, self.template)
        self.assertTemplateUsed(response, "circulation_desk/base.html")

    # Test Page features.
    def test_page_has_content(self):
        """
        Check page for specific fields when logged in
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = TC_NSEC
        session.save()
        response = self.client.get(self.url)
        for item in self.content:
            self.assertIn(item.encode(), response.content)
        
        # Clear session and test login with just NPUB
        session.clear()
        session.save()
        self.assertNotIn("npub", session)
        self.assertNotIn("nsec", session)
        session["npub"] = TC_NPUB
        session.save()
        response = self.client.get(self.url)

        if self.readonly:
            self.assertIn(b"Unavailable in Read-Only Mode", response.content)
        else:
            for item in self.content:
                self.assertIn(item.encode(), response.content)
    
    # Test page redirects when not logged in
    def test_page_redirects(self):
        """
        Test page redirects when not logged in
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)