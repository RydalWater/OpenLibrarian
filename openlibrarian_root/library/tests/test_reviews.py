from django.test import TestCase, Client
import io, sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from hashlib import sha256
from time import sleep
from circulation_desk.tests.test_index import TC_NPUB, TC_NSEC, TC_RELAYS, TC_LIBRARIES, TC_PROGRESS, TC_ISBNS, TC_REVIEWS

class ReviewsFunctionalTestCase(TestCase):
    """
    Functional Tests for the reviews page
    """
    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.url = "/library/reviews/"
        self.driver = webdriver.Firefox()
        self.driver.get(f"http://127.0.0.1:8000/login-npub/")
        self.driver.find_element(by=By.ID, value="npub").send_keys("npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n")
        self.driver.find_element(by=By.ID, value="login").click()

    def test_reviews_back(self):
        """
        Test Reviews Back Button
        """
        sleep(5)
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="back").click()
        self.assertIn("/library/", self.driver.current_url)
    
    def tearDown(self):
        """
        Tear Down function to close driver
        """
        self.driver.close()

class ReviewsUnitTestCase(TestCase):
    """
    Unit Tests for the reviews page
    """

    def setUp(self):
        self.url = "/library/reviews/"
        self.template = "library/reviews.html"
        self.content = ["Reviews", "Back", "Refresh", "Guide to Outdoor Clues and Signs"]
        self.client = Client()
        self.readonly = False

    def test_page_returns_200(self):
        """
        Page returns a 200 response when logged in
        """

        # Set session with login both NPUB and NSEC
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session["libraries"] = TC_LIBRARIES
        session["reviews"] = TC_REVIEWS
        session.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        # Clear session and test login with just NPUB
        session.clear()
        session.save()
        self.assertNotIn("npub", session)
        self.assertNotIn("nsec", session)
        session["npub"] = TC_NPUB
        session["libraries"] = TC_LIBRARIES
        session["reviews"] = TC_REVIEWS
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
        session["nsec"] = "Y"
        session["libraries"] = TC_LIBRARIES
        session["reviews"] = TC_REVIEWS
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
        session["libraries"] = TC_LIBRARIES
        session["reviews"] = TC_REVIEWS
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
        session["nsec"] = "Y"
        session["libraries"] = TC_LIBRARIES
        session["reviews"] = TC_REVIEWS
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
        session["libraries"] = TC_LIBRARIES
        session["reviews"] = TC_REVIEWS
        session.save()
        response = self.client.get(self.url)

        for item in self.content:
            self.assertIn(item.encode(), response.content)
        
        # Check content when no reviews/library data
        session.clear()
        session.save()
        self.assertNotIn("npub", session)
        self.assertNotIn("nsec", session)
        session["npub"] = TC_NPUB
        session["libraries"] = {}
        session["reviews"] = {}
        session.save()
        response = self.client.get(self.url)
        self.assertIn(b"You currently have no books to review.", response.content)
    
    # Test page redirects when not logged in
    def test_page_redirects(self):
        """
        Test page redirects when not logged in
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
    
    # Test Post add review
    def test_post_add_review(self):
        """
        Test post request
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session["libraries"] = TC_LIBRARIES
        session["reviews"] = TC_REVIEWS
        session.save()
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        response = self.client.post(self.url, {"book_info": "e1d342f8901e9db6dcd671b974e130f8bc5353f7-9781444780109", "comments": "Really thought this book was great!", "rating" : "6"})
        sys.stdout = sys.__stdout__
        self.assertEqual(response.status_code, 200)
        rcontext = response.context["session"]["reviews"]
        note = response.context["noted"]
        self.assertEqual(note, None)
        self.assertEqual(rcontext["9781444780109"]["id"], sha256("9781444780109".encode()).hexdigest())
        self.assertEqual(rcontext["9781444780109"]["exid"], "isbn")
        self.assertEqual(rcontext["9781444780109"]["rating"], 3.0)
        self.assertEqual(rcontext["9781444780109"]["content"], "Really thought this book was great!")
        self.assertEqual(rcontext["9781444780109"]["tags"], [])
        self.assertEqual(rcontext["9781444780109"]["rating_normal"], "0.6")
        self.assertEqual(rcontext["9781444780109"]["rating_raw"], "3.0/5")

    # Test post with invalid data
    def test_post_invalid_data(self):
        """
        Test post request with invalid data
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session["libraries"] = TC_LIBRARIES
        session["reviews"] = TC_REVIEWS
        session.save()
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        response = self.client.post(self.url, {"book_info": "e1d342f8901e9db6dcd671b974e130f8bc5353f7-9781444780109"})
        sys.stdout = sys.__stdout__
        self.assertEqual(response.status_code, 200)
        note = response.context["noted"]
        self.assertEqual(note, "false:Error rating book, please refresh and try again.")
    
    # Test refresh post
    def test_post_refresh(self):
        """
        Test post request for refresh
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session["libraries"] = TC_LIBRARIES
        session["reviews"] = TC_REVIEWS
        session["relays"] = TC_RELAYS
        session.save()
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        response = self.client.post(self.url, {"book_info": "e1d342f8901e9db6dcd671b974e130f8bc5353f7-9781444780109", "comments": "Really thought this book was great!", "rating" : "6"})
        sleep(1)
        response = self.client.post(self.url, {"refresh": "refresh"})
        sleep(2)
        sys.stdout = sys.__stdout__
        self.assertEqual(response.status_code, 200)
        note = response.context["noted"]
        self.assertEqual(note, None)

        rcontext = response.context["session"]["reviews"]

        refresh_reviews = {}
        for isbn in TC_ISBNS:
            refresh_reviews[isbn] = {
                "id": sha256(isbn.encode()).hexdigest(),
                "exid": "isbn",
                "rating": None,
                "content": "",
                "tags": [],
                "rating_normal": "NA",
                "rating_raw": "NA"
            }
            
        for isbn in TC_ISBNS:
            self.assertEqual(rcontext[isbn]["id"], sha256(isbn.encode()).hexdigest())
            self.assertEqual(rcontext[isbn]["exid"], "isbn")
            self.assertEqual(rcontext[isbn]["rating"], None)
            self.assertEqual(rcontext[isbn]["content"], "")
            self.assertEqual(rcontext[isbn]["tags"], [])
            self.assertEqual(rcontext[isbn]["rating_normal"], "NA")
            self.assertEqual(rcontext[isbn]["rating_raw"], "NA")
            self.assertEqual(rcontext[isbn], refresh_reviews[isbn])

