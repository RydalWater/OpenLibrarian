from django.test import TestCase, Client
from almanac.tests.test_settings import SettingsUnitTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep


class FriendsFunctionalTestCase(TestCase):
    """
    Functional Tests for the Friends page
    """
    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.url = "/almanac/friends/"
        self.driver = webdriver.Firefox()
        self.driver.get(f"http://127.0.0.1:8000/login-npub/")
        self.driver.find_element(by=By.ID, value="npub").send_keys("npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n")
        self.driver.find_element(by=By.ID, value="submit").click()
        sleep(1)

    def test_almanac_relays(self):
        """
        Test Relays Back Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="back").click()
        self.assertIn("/almanac/", self.driver.current_url)
    
    def tearDown(self):
        """
        Tear Down function to close driver
        """
        self.driver.close()

class FriendsUnitTestCase(SettingsUnitTestCase):
    """
    Unit Tests for the Friends page
    """
    def setUp(self):
        self.url = "/almanac/friends/"
        self.template = "almanac/user_friends.html"
        self.content = ["Friends", "Foes (Muted)", "Back"]
        self.client = Client()
        self.readonly = False

    def test_content_logged_in(self):
        """
        Check page for specific fields when logged in
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session.save()
        response = self.client.get(self.url)
        for item in ["Refresh", "Enter a Users Public Key or NIP05 Address"]:
            self.assertIn(item.encode(), response.content)
        
    def test_context(self):
        """
        Test context fields
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session.save()
        response = self.client.get(self.url)
        for item in ["session", "friends", "muted", "notification"]:
            self.assertIn(item, response.context.keys())

    def test_post_follow(self):
        """
        Test post request (with follow)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session.save()
        response = self.client.post(self.url, {"follow": "Follow"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["notification"], "Please provide npub or nip05.")

    def test_post_follow_user(self):
        """
        Test post request (with follow_user)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session.save()
        response = self.client.post(self.url, {"follow_user": "npub1tea3zvjl2cv32p8j2098hmq9qf7lqqmddv0ruzjgqjjxa8x4z8qqec9s5z"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["notification"], None)

    def test_post_follow_user_invalid(self):
        """
        Test post request (with follow_user invalid)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session.save()
        response = self.client.post(self.url, {"follow_user": "apple"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["notification"], "Invalid npub or nip05.")

    def test_post_refresh(self):
        """
        Test post request (with refresh)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session.save()
        response = self.client.post(self.url, {"refresh": "Refresh"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["notification"], "Refreshed.")

    def test_post_other(self):
        """
        Test post request (with other)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session.save()
        with self.assertRaises(Exception) as cm:
            self.client.post(self.url, {"other": "Some other value"})

        # Check that the exception message is correct
        self.assertEqual(str(cm.exception), "Invalid request.")