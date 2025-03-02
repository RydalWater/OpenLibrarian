from django.test import TestCase, Client
from almanac.tests.test_settings import SettingsUnitTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from nostr_sdk import Keys
from circulation_desk.tests.test_index import TC_NPUB

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
        self.driver.find_element(by=By.ID, value="npub").send_keys(TC_NPUB)
        self.driver.find_element(by=By.ID, value="login").click()

    def test_almanac_friends_back(self):
        """
        Test Friend Back Button
        """
        sleep(5)
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
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session.save()
        response = self.client.get(self.url)
        for item in ["Refresh", "Enter a Users Public Key or NIP05 Address"]:
            self.assertIn(item.encode(), response.content)
        
    def test_context(self):
        """
        Test context fields
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session.save()
        response = self.client.get(self.url)
        for item in ["session", "friends", "muted", "noted"]:
            self.assertIn(item, response.context.keys())

    def test_post_follow(self):
        """
        Test post request (with follow)
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session.save()
        response = self.client.post(self.url, {"follow": "Follow"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["noted"], "false:Please provide npub or nip05.")

    def test_post_follow_user(self):
        """
        Test post request (with follow_user)
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session.save()
        response = self.client.post(self.url, {"follow_user": "npub1tea3zvjl2cv32p8j2098hmq9qf7lqqmddv0ruzjgqjjxa8x4z8qqec9s5z"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["noted"], None)

    def test_post_follow_user_invalid(self):
        """
        Test post request (with follow_user invalid)
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session.save()
        response = self.client.post(self.url, {"follow_user": "apple"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["noted"], "false:Invalid npub or nip05.")

    def test_post_refresh(self):
        """
        Test post request (with refresh)
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session.save()
        response = self.client.post(self.url, {"refresh": "Refresh"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["noted"], "true:Refreshed.")
    
    def test_post_remove_invalid(self):
        """
        Test post request (with remove) invalid
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session.save()
        response = self.client.post(self.url, {"remove": "apple"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["noted"], "false:Invalid npub.")


    def test_post_remove_not_follow(self):
        """
        Test post request (with remove) not following
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        keys = Keys.generate()
        session.save()
        response = self.client.post(self.url, {"remove": keys.public_key().to_bech32()})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["noted"], "false:Not Following.")
    
    # TODO: Add remove test for followed user.