from django.test import TestCase, Client
from almanac.tests.test_settings import SettingsUnitTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep


class ProfileFunctionalTestCase(TestCase):
    """
    Functional Tests for the profile page
    """
    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.url = "/almanac/profile/"
        self.driver = webdriver.Firefox()
        self.driver.get(f"http://127.0.0.1:8000/login-npub/")
        self.driver.find_element(by=By.ID, value="npub").send_keys("npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n")
        self.driver.find_element(by=By.ID, value="submit").click()
        sleep(1)

    def test_almanac_profile(self):
        """
        Test Profile Back Button
        """
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="back").click()
        self.assertIn("/almanac/", self.driver.current_url)
    
    def tearDown(self):
        """
        Tear Down function to close driver
        """
        self.driver.close()

class ProfileUnitTestCase(SettingsUnitTestCase):
    """
    Unit Tests for the profile page
    """
    def setUp(self):
        self.url = "/almanac/profile/"
        self.template = "almanac/user_profile.html"
        self.content = ["Account Nym", "Display Name", "About", "Profile Picture", "NIP05"]
        self.client = Client()
        self.readonly = True

    def test_get(self):
        """
        Test get request for None notification
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["notification"], None)
        self.assertIn("session",response.context.keys())
    
    def test_post_refresh(self):
        """
        Test post request for refresh
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session.save()
        response = self.client.post(self.url, {"refresh": "Refresh"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("session",response.context.keys())

        # Test refresh with relays in session
        session["relays"] = {"wss://relay.damus.io": None, "wss://nostr.mom": "READ"}
        session.save()
        response = self.client.post(self.url, {"refresh": "Refresh"})
        self.assertEqual(response.status_code, 200)

    def test_post_save(self):
        """
        Test post request for save
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session["profile"] = {
            "nym" : "test_nym",
            "displayname" : "test_display_name",
            "about" : "test_about",
            "picture" : None,
            "nip05" : None,
            "website" : None,
            "banner" : None,
            "lud06" : None,
            "lud16" : None,
        }
        session.save()
        response = self.client.post(self.url, {"save": "Save"})
        self.assertEqual(response.status_code, 200)

    def test_post_save_nym(self):
        """
        Test post request for save (edit nym)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session["profile"] = {
            "nym" : "test_nym",
            "displayname" : "test_display_name",
            "about" : "test_about",
            "picture" : None,
            "nip05" : None,
            "website" : None,
            "banner" : None,
            "lud06" : None,
            "lud16" : None,
        }
        session.save()
        # Update nym and retry
        response = self.client.post(self.url, {"save": "Save", "edit_nym": "new_nym"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["session"]["profile"]["nym"], "new_nym")

    def test_post_save_displayname(self):
        """
        Test post request for save (edit display name)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session["profile"] = {
            "nym" : "test_nym",
            "displayname" : "test_display_name",
            "about" : "test_about",
            "picture" : None,
            "nip05" : None,
            "website" : None,
            "banner" : None,
            "lud06" : None,
            "lud16" : None,
        }
        session.save()
        # Update display name and retry
        response = self.client.post(self.url, {"save": "Save", "edit_displayname": "new_display_name"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["session"]["profile"]["displayname"], "new_display_name")

    def test_post_save_about(self):
        """
        Test post request for save (edit about)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session["profile"] = {
            "nym" : "test_nym",
            "displayname" : "test_display_name",
            "about" : "test_about",
            "picture" : None,
            "nip05" : None,
            "website" : None,
            "banner" : None,
            "lud06" : None,
            "lud16" : None,
        }
        session.save()
        # Update about and retry
        response = self.client.post(self.url, {"save": "Save", "edit_about": "new_about"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["session"]["profile"]["about"], "new_about")
    
    def test_post_save_picture(self):
        """
        Test post request for save (edit picture)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session["profile"] = {
            "nym" : "test_nym",
            "displayname" : "test_display_name",
            "about" : "test_about",
            "picture" : None,
            "nip05" : None,
            "website" : None,
            "banner" : None,
            "lud06" : None,
            "lud16" : None,
        }
        session.save()
        # Update profile picture and retry
        response = self.client.post(self.url, {"save": "Save", "edit_picture": "https://pfp.nostr.build/9d45acc985222226824a1e91850bf3d450b8b5964ef14f41fbd4df2c9dcc3241.jpg"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["session"]["profile"]["picture"], "https://pfp.nostr.build/9d45acc985222226824a1e91850bf3d450b8b5964ef14f41fbd4df2c9dcc3241.jpg")
    
    def test_post_save_nip05(self):
        """
        Test post request for save (edit NIP05)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session["profile"] = {
            "nym" : "test_nym",
            "displayname" : "test_display_name",
            "about" : "test_about",
            "picture" : None,
            "nip05" : None,
            "website" : None,
            "banner" : None,
            "lud06" : None,
            "lud16" : None,
        }
        session.save()
        # Update NIP05 and retry
        response = self.client.post(self.url, {"save": "Save", "edit_nip05": "Rydal@gitlurker.info"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["session"]["profile"]["nip05"], "Rydal@gitlurker.info")