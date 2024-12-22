from django.test import TestCase, Client
from almanac.tests.test_settings import SettingsUnitTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep


class RelaysFunctionalTestCase(TestCase):
    """
    Functional Tests for the relays page
    """
    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.url = "/almanac/relays/"
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

class RelaysUnitTestCase(TestCase):
    """
    Unit Tests for the relays page
    """
    def setUp(self):
        self.url = "/almanac/relays/"
        self.template = "almanac/user_relays.html"
        self.content = ["Relays", "Back"]
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
        for item in ["Add Relay", "Read", "Write", "Both", "Cancel", "Save"]:
            self.assertIn(item.encode(), response.content)

    def test_post(self):
        """
        Test post request
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session.save()
        response = self.client.post(self.url, {"post": ""})
        self.assertEqual(response.status_code, 200)

    def test_post_remove(self):
        """
        Test post request remove (valid)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session["relays"] = {"wss://relay.damus.io": None, "wss://nostr.mom": "READ"}
        session.save()
        response1_mod = self.client.get(self.url).context["mod_relays"]
        response = self.client.post(self.url, {"remove": "wss://nostr.mom"})
        response2_mod = response.context["mod_relays"]
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response1_mod, response2_mod)
        self.assertNotIn("wss://nostr.mom", response2_mod)

    def test_post_remove_write(self):
        """
        Test post request remove (invalid - no write)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session["relays"] = {"wss://relay.damus.io": None, "wss://nostr.mom": "READ"}
        session.save()
        response1_mod = self.client.get(self.url).context["mod_relays"]
        response = self.client.post(self.url, {"remove": "wss://relay.damus.io"})
        response2_mod = response.context["mod_relays"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response1_mod, response2_mod)
    
    def test_post_remove_read(self):
        """
        Test post request remove (invalid - no read)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session["relays"] = {"wss://relay.damus.io": None, "wss://nostr.mom": "WRITE"}
        session.save()
        response1_mod = self.client.get(self.url).context["mod_relays"]
        response = self.client.post(self.url, {"remove": "wss://relay.damus.io"})
        response2_mod = response.context["mod_relays"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response1_mod, response2_mod)
    
    def test_post_add_read(self):
        """
        Test post request add (read)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session["relays"] = {"wss://relay.damus.io": None}
        session.save()
        response1_mod = self.client.get(self.url).context["mod_relays"]
        response = self.client.post(self.url, {"add_relay": "Add", "add_relay_url": "wss://nostr.mom", "relay_option": "R"})
        response2_mod = response.context["mod_relays"]
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response1_mod, response2_mod)
        self.assertIn("wss://nostr.mom", response2_mod)
    
    def test_post_add_write(self):
        """
        Test post request add (write)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session["relays"] = {"wss://relay.damus.io": None}
        session.save()
        response1_mod = self.client.get(self.url).context["mod_relays"]
        response = self.client.post(self.url, {"add_relay": "Add", "add_relay_url": "wss://nostr.mom", "relay_option": "W"})
        response2_mod = response.context["mod_relays"]
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response1_mod, response2_mod)
        self.assertIn("wss://nostr.mom", response2_mod)
    
    def test_post_add_both(self):
        """
        Test post request add (both)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session["relays"] = {"wss://relay.damus.io": None}
        session.save()
        response1_mod = self.client.get(self.url).context["mod_relays"]
        response = self.client.post(self.url, {"add_relay": "Add", "add_relay_url": "wss://nostr.mom", "relay_option": "B"})
        response2_mod = response.context["mod_relays"]
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response1_mod, response2_mod)
        self.assertIn("wss://nostr.mom", response2_mod)
    
    def test_post_save_invalid(self):
        """
        Test post request for save (invalid)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["relays"] = {"wss://relay.damus.io": None}
        session["mod_relays"] = {"wss://relay.damus.io": None, "wss://nostr.mom": None}
        session.save()
        response = self.client.post(self.url, {"save": "Save"})
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.context["relays"], response.context["mod_relays"])

    def test_post_save_valid(self):
        """
        Test post request for save (valid)
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session["relays"] = {"wss://relay.damus.io": None}
        session["mod_relays"] = {"wss://relay.damus.io": None, "wss://nostr.mom": None}
        session.save()
        response = self.client.post(self.url, {"save": "Save"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["relays"], response.context["mod_relays"])
    
    def test_post_cancel(self):
        """
        Test post request for cancel
        """
        session = self.client.session
        session["npub"] = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        session["nsec"] = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        session["relays"] = {"wss://relay.damus.io": None}
        session["mod_relays"] = {"wss://relay.damus.io": None, "wss://nostr.mom": None}
        session.save()
        response = self.client.post(self.url, {"cancel": "Cancel"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["relays"], response.context["mod_relays"])