from django.test import TestCase, Client
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep


class LibraryFunctionalTestCase(TestCase):
    """
    Functional Tests for the library page
    """
    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.url = "/library/"
        self.driver = webdriver.Firefox()
        self.driver.get(f"http://127.0.0.1:8000/login-npub/")
        self.driver.find_element(by=By.ID, value="npub").send_keys("npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n")
        self.driver.find_element(by=By.ID, value="login").click()

    def test_library_shelves(self):
        """
        Test Library Shelves Button
        """
        sleep(10)
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="shelves").click()
        self.assertIn("/shelves/", self.driver.current_url)
    
    def tearDown(self):
        """
        Tear Down function to close driver
        """
        self.driver.close()

class LibraryUnitTestCase(TestCase):
    """
    Unit Tests for the settings page
    """
    def setUp(self):
        self.url = "/library/"
        self.template = "library/library.html"
        self.content = ["Library", "Shelves", "Reviews", "Statistics"]
        self.client = Client()
        self.readonly = False

    
    # Test page returns a 200 response
    def test_page_returns_200(self):
        """
        Page returns a 200 response when logged in
        """

        # Set session with login both NPUB and NSEC
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        # Clear session and test login with just NPUB
        session.clear()
        session.save()
        self.assertNotIn("npub", session)
        self.assertNotIn("nsec", session)
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    # Test template is correct
    def test_page_template(self):
        """
        Check page templates (inc. base.html) when logged in
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session.save()
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, self.template)
        self.assertTemplateUsed(response, "circulation_desk/base.html")

        # Clear session and test login with just NPUB
        session.clear()
        session.save()
        self.assertNotIn("npub", session)
        self.assertNotIn("nsec", session)
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
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
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session.save()
        response = self.client.get(self.url)
        for item in self.content:
            self.assertIn(item.encode(), response.content)
        
        # Clear session and test login with just NPUB
        session.clear()
        session.save()
        self.assertNotIn("npub", session)
        self.assertNotIn("nsec", session)
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session.save()
        response = self.client.get(self.url)

        for item in self.content:
            self.assertIn(item.encode(), response.content)
            
    
    # Test page redirects when not logged in
    def test_page_redirects(self):
        """
        Test page redirects when not logged in
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)