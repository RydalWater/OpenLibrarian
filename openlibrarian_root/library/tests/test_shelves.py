from django.test import TestCase, Client
import datetime, io, sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from hashlib import sha256
from time import sleep
from circulation_desk.tests.test_index import TC_NPUB, TC_NSEC, TC_RELAYS, TC_LIBRARIES, TC_PROGRESS

class ShelvesFunctionalTestCase(TestCase):
    """
    Functional Tests for the shelves page
    """
    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.url = "/library/shelves/"
        self.driver = webdriver.Firefox()
        self.driver.get(f"http://127.0.0.1:8000/login-npub/")
        self.driver.find_element(by=By.ID, value="npub").send_keys(TC_NPUB)
        self.driver.find_element(by=By.ID, value="login").click()

    def test_shelves_back(self):
        """
        Test Shelves Back Button
        """
        sleep(5)
        self.driver.get(f"http://127.0.0.1:8000{self.url}")
        self.driver.find_element(by=By.ID, value="back").click()
        self.assertIn("/library/", self.driver.current_url)
    
    # TODO: Add a few more functional tests to check that the shelves pages work as expected (inc modals)

    def tearDown(self):
        """
        Tear Down function to close driver
        """
        self.driver.close()

class ShelvesUnitTestCase(TestCase):
    """
    Unit Tests for the shelves page
    """
    def setUp(self):
        self.url = "/library/shelves/"
        self.template = "library/library_shelves.html"
        self.content = ["Shelves", "Back", "Refresh", "Currently Reading", "On the Shelf", "Want to Read", "Finished"]
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
        session["nsec"] = "Y"
        session["libraries"] = TC_LIBRARIES
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
    
    def test_library_refresh_post(self):
        """
        Test Library Fetch logged in
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session["relays"] = TC_RELAYS
        session.save()
        data = {'refresh': 'shelves', 'npubValue': TC_NPUB}
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertIn("progress", response.context)
        self.assertIn("libraries", response.context)
        self.assertEqual(4, len(response.context["libraries"]))
        self.assertEqual(response.context["noted"], None)
    
    def test_library_fetch_none(self):
        """
        Test Library Fetch (none libs) logged in
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session["relays"] = TC_RELAYS
        session["libraries"] = None
        session.save()
        response = self.client.get(self.url)
        self.assertIn("progress", response.context)
        self.assertIn("libraries", response.context)
        self.assertEqual(4, len(response.context["libraries"]))
        self.assertEqual(response.context["noted"], None)
    
    def test_library_fetch_miss(self):
        """
        Test Library Fetch (missing libs) logged in
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session["relays"] = TC_RELAYS
        session.save()
        response = self.client.get(self.url)
        self.assertIn("progress", response.context)
        self.assertIn("libraries", response.context)
        self.assertEqual(4, len(response.context["libraries"]))
        self.assertEqual(response.context["noted"], None)
    
    def test_library_read_only(self):
        """
        Test Library Fetch (read only) not logged in
        """
        session = self.client.session
        session["npub"] = "npub1039j8zfxafe5xtx5qhmjf02rv7upgwgx54kd35e5qehj36egkjuqx9f704"
        session["nsec"] = None
        session["relays"] = TC_RELAYS
        session["libraries"] = TC_LIBRARIES
        session.save()
        data = {'refresh': 'shelves', 'npubValue': "npub1039j8zfxafe5xtx5qhmjf02rv7upgwgx54kd35e5qehj36egkjuqx9f704"}
        response = self.client.post(self.url, data, content_type='application/json')
        visible_isbns = []
        for library in response.context["libraries"]:
            for book in library["b"]:
                if book["h"] == "Y":
                    self.assertIn("Hidden",book["i"])
                else:
                    if library["s"] in ["CR", "HR"]:
                        visible_isbns.append(book["i"])
        
        for each in visible_isbns:
            self.assertIn(each, response.context["progress"].keys())
        

    def test_library_post_remove(self):
        """
        Test Library Remove Book logged in
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session["relays"] = TC_RELAYS
        session["libraries"] = TC_LIBRARIES
        session.save()
        response = self.client.get(self.url)
        for library in response.context["libraries"]:
            if library["i"] == "fe7046323fc3ccc7c6b2748ba58295fc4206a1a3":
                for book in library["b"]:
                    self.assertEqual("9780007560776", book["i"])
                break
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        response = self.client.post(self.url, {"remove_book": "true", "book_info":"fe7046323fc3ccc7c6b2748ba58295fc4206a1a3-9780007560776"})
        sys.stdout = sys.__stdout__
        for library in response.context["libraries"]:
            if library["i"] == "fe7046323fc3ccc7c6b2748ba58295fc4206a1a3":
                for book in library["b"]:
                    self.assertNotEqual("9780007560776", book["i"])
                break
    
    def test_library_post_moved_to_cr_from_trw(self):
        """
        Test Library move book to CR shelf from TRW
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session["relays"] = TC_RELAYS
        session["libraries"] = TC_LIBRARIES
        session["progress"] = TC_PROGRESS
        session.save()
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        response = self.client.post(self.url, {"moved": "true", "book_info":"f76a2d0c13b20a32eeefc4e4f5b393f7b0d6dccc-9780718183899", "status":"CR"})
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        cr_books = []
        for library in response.context["libraries"]:
            if library["i"] == "f76a2d0c13b20a32eeefc4e4f5b393f7b0d6dccc":
                old_lib = library
            elif library["i"] == "fe7046323fc3ccc7c6b2748ba58295fc4206a1a3":
                for book in library["b"]:
                    cr_books.append(book["i"])

        stDt = datetime.datetime.now().strftime("%Y-%m-%d")
        self.assertEqual(["9780007560776","9780718183899"], cr_books)
        self.assertIn("9780718183899", response.context["progress"].keys())
        self.assertEqual(response.context["progress"]["9780718183899"]["id"], sha256("9780718183899".encode()).hexdigest())
        self.assertEqual(response.context["progress"]["9780718183899"]["exid"], "isbn")
        self.assertEqual(response.context["progress"]["9780718183899"]["curr"], "0")
        self.assertEqual(response.context["progress"]["9780718183899"]["max"], "320")
        self.assertEqual(response.context["progress"]["9780718183899"]["st"], stDt)
        self.assertEqual(response.context["progress"]["9780718183899"]["en"], "NA")
        self.assertEqual(response.context["progress"]["9780718183899"]["unit"], "pages")
        self.assertEqual(response.context["progress"]["9780718183899"]["progress"], "0")
        self.assertEqual(response.context["progress"]["9780718183899"]["default"], "320")
        for book in old_lib["b"]:
            self.assertNotEqual("9780718183899", book["i"])
        
    def test_library_post_moved_to_hr_from_trw(self):
        """
        Test Library move book to HR shelf TRW
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session["relays"] = TC_RELAYS
        session["libraries"] = TC_LIBRARIES
        session["progress"] = TC_PROGRESS
        session.save()
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        response = self.client.post(self.url, {"moved": "true", "book_info":"f76a2d0c13b20a32eeefc4e4f5b393f7b0d6dccc-9780718183899", "status":"HR"})
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        hr_books = []
        for library in response.context["libraries"]:
            if library["i"] == "fe7046323fc3ccc7c6b2748ba58295fc4206a1a3":
                old_lib = library
            elif library["i"] == "e1d342f8901e9db6dcd671b974e130f8bc5353f7":
                for book in library["b"]:
                    hr_books.append(book["i"])

        stDt = datetime.datetime.now().strftime("%Y-%m-%d")
        enDt = stDt
        self.assertEqual(["9781444780109", "9781408898956", "0140232699", "9780718183899"], hr_books)
        self.assertIn("9780718183899", response.context["progress"].keys())
        self.assertEqual(response.context["progress"]["9780718183899"]["id"], sha256("9780718183899".encode()).hexdigest())
        self.assertEqual(response.context["progress"]["9780718183899"]["exid"], "isbn")
        self.assertEqual(response.context["progress"]["9780718183899"]["curr"], "320")
        self.assertEqual(response.context["progress"]["9780718183899"]["max"], "320")
        self.assertEqual(response.context["progress"]["9780718183899"]["st"], stDt)
        self.assertEqual(response.context["progress"]["9780718183899"]["en"], enDt)
        self.assertEqual(response.context["progress"]["9780718183899"]["unit"], "pages")
        self.assertEqual(response.context["progress"]["9780718183899"]["progress"], "100")
        self.assertEqual(response.context["progress"]["9780718183899"]["default"], "320")
        for book in old_lib["b"]:
            self.assertNotEqual("9780718183899", book["i"])
    
    def test_library_post_moved_to_trs_from_trw(self):
        """
        Test Library move book to TRS shelf TRW
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session["relays"] = TC_RELAYS
        session["libraries"] = TC_LIBRARIES
        session["progress"] = TC_PROGRESS
        session.save()
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        response = self.client.post(self.url, {"moved": "true", "book_info":"f76a2d0c13b20a32eeefc4e4f5b393f7b0d6dccc-9780718183899", "status":"TRS"})
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        trs_books = []
        for library in response.context["libraries"]:
            if library["i"] == "f76a2d0c13b20a32eeefc4e4f5b393f7b0d6dccc":
                old_lib = library
            elif library["i"] == "aea571dbde5eb6ebec93c91b95486539b9491962":
                for book in library["b"]:
                    trs_books.append(book["i"])

        self.assertEqual(["0349114749","1857987225","9781407104256", "0007165870", "9780718183899"], trs_books)
        self.assertNotIn("9780718183899", response.context["progress"].keys())
        for book in old_lib["b"]:
            self.assertNotEqual("9780718183899", book["i"])
   
    def test_library_post_move_from_cr_to_hr(self):
        """
        Test Library move book from CR to HR
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session["relays"] = TC_RELAYS
        session["libraries"] = TC_LIBRARIES
        session["progress"] = TC_PROGRESS
        session["reviews"] = {}
        session.save()
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        response = self.client.post(self.url, {"moved": "true", "book_info":"fe7046323fc3ccc7c6b2748ba58295fc4206a1a3-9780007560776", "status":"4"})
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        hr_books = []
        for library in response.context["libraries"]:
            if library["i"] == "fe7046323fc3ccc7c6b2748ba58295fc4206a1a3":
                old_lib = library
            elif library["i"] == "e1d342f8901e9db6dcd671b974e130f8bc5353f7":
                for book in library["b"]:
                    hr_books.append(book["i"])
        stDt = datetime.datetime.now().strftime("%Y-%m-%d")
        enDt = stDt
        self.assertEqual(["9781444780109", "9781408898956", "0140232699", "9780007560776"], hr_books)
        self.assertIn("9780007560776", response.context["progress"].keys())
        self.assertEqual(response.context["progress"]["9780007560776"]["id"], sha256("9780007560776".encode()).hexdigest())
        self.assertEqual(response.context["progress"]["9780007560776"]["exid"], "isbn")
        self.assertEqual(response.context["progress"]["9780007560776"]["curr"], "100")
        self.assertEqual(response.context["progress"]["9780007560776"]["max"], "100")
        self.assertEqual(response.context["progress"]["9780007560776"]["st"], stDt)
        self.assertEqual(response.context["progress"]["9780007560776"]["en"], enDt)
        self.assertEqual(response.context["progress"]["9780007560776"]["unit"], "pct")
        self.assertEqual(response.context["progress"]["9780007560776"]["progress"], "100")
        self.assertEqual(response.context["progress"]["9780007560776"]["default"], "NOT AVAILABLE")
        self.assertEqual([], old_lib["b"])

    def test_library_post_move_from_hr_to_cr(self):
        """
        Test Library move book from HR to CR
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session["relays"] = TC_RELAYS
        session["libraries"] = TC_LIBRARIES
        session["progress"] = TC_PROGRESS
        session.save()
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        response = self.client.post(self.url, {"moved": "true", "book_info":"e1d342f8901e9db6dcd671b974e130f8bc5353f7-9781444780109", "status":"CR"})
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        cr_books = []
        for library in response.context["libraries"]:
            if library["i"] == "e1d342f8901e9db6dcd671b974e130f8bc5353f7":
                old_lib = library
            elif library["i"] == "fe7046323fc3ccc7c6b2748ba58295fc4206a1a3":
                for book in library["b"]:
                    cr_books.append(book["i"])
        stDt = datetime.datetime.now().strftime("%Y-%m-%d")
        self.assertEqual(["9780007560776", "9781444780109"], cr_books)
        self.assertIn("9781444780109", response.context["progress"].keys())
        self.assertEqual(response.context["progress"]["9781444780109"]["id"], sha256("9781444780109".encode()).hexdigest())
        self.assertEqual(response.context["progress"]["9781444780109"]["exid"], "isbn")
        self.assertEqual(response.context["progress"]["9781444780109"]["curr"], "0")
        self.assertEqual(response.context["progress"]["9781444780109"]["max"], "100")
        self.assertEqual(response.context["progress"]["9781444780109"]["st"], stDt)
        self.assertEqual(response.context["progress"]["9781444780109"]["en"], "NA")
        self.assertEqual(response.context["progress"]["9781444780109"]["unit"], "pct")
        self.assertEqual(response.context["progress"]["9781444780109"]["progress"], "0")
        self.assertEqual(response.context["progress"]["9781444780109"]["default"], "NOT AVAILABLE")
        for book in old_lib["b"]:
            self.assertNotEqual("9781444780109", book["i"])
    
    def test_library_post_update_invalid_dates(self):
        """
        Test Library update invalid dates
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session["relays"] = TC_RELAYS
        session["libraries"] = TC_LIBRARIES
        session["progress"] = TC_PROGRESS
        session.save()
        response = self.client.post(self.url, {"update": "true", "book_info":"f76a2d0c13b20a32eeefc4e4f5b393f7b0d6dccc-9780718183899", "stDt":"2023-01-02", "enDt":"2023-01-01"})
        self.assertEqual("false:End date is before start date.", response.context["noted"])

        response = self.client.post(self.url, {"update": "true", "book_info":"f76a2d0c13b20a32eeefc4e4f5b393f7b0d6dccc-9780718183899", "stDt":"NA", "enDt":"2023-01-01"})
        self.assertEqual("false:Start date is required when adding end date.", response.context["noted"])

    def test_library_post_update_invalid_progress(self):    
        """
        Test Library update invalid progress
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session["relays"] = TC_RELAYS
        session["libraries"] = TC_LIBRARIES
        session["progress"] = TC_PROGRESS
        session.save()
        response = self.client.post(self.url, {"update": "true", "book_info":"f76a2d0c13b20a32eeefc4e4f5b393f7b0d6dccc-9780718183899", "unitRadio":"pages", "maxPage":"100", "currentPage":"101"})
        self.assertEqual("false:Current progress is greater than max.", response.context["noted"])

    def test_library_post_update_valid_unit(self):
        """
        Test Library update valid unit
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session["relays"] = TC_RELAYS
        session["libraries"] = TC_LIBRARIES
        session["progress"] = TC_PROGRESS
        session.save()
        stDt = datetime.datetime.now().strftime("%Y-%m-%d")
        response = self.client.get(self.url)
        self.assertEqual(response.context["progress"]["9780007560776"]["unit"], "pct")
    
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        response = self.client.post(self.url, {"update": "true", "book_info":"fe7046323fc3ccc7c6b2748ba58295fc4206a1a3-9780007560776", "unitRadio":"pages", "maxPage":"100", "currentPage":"50"}, follow=True)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        self.assertEqual(response.context["progress"]["9780007560776"]["unit"], "pages")

        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        response = self.client.post(self.url, {"update": "true", "book_info":"fe7046323fc3ccc7c6b2748ba58295fc4206a1a3-9780007560776", "unitRadio":"pct", "maxPct":"100", "currentPct":"50"}, follow=True)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        self.assertEqual(response.context["progress"]["9780007560776"]["unit"], "pct")


    def test_library_post_update_valid_start(self):
        """
        Test Library update valid start date
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session["relays"] = TC_RELAYS
        session["libraries"] = TC_LIBRARIES
        session["progress"] = TC_PROGRESS
        session.save()
        response = self.client.get(self.url)
        self.assertEqual(response.context["progress"]["9780007560776"]["st"], "NA")

        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        response = self.client.post(self.url, {"update": "true", "book_info":"fe7046323fc3ccc7c6b2748ba58295fc4206a1a3-9780007560776", "stDt":"2023-01-02"}, follow=True)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        self.assertEqual(response.context["progress"]["9780007560776"]["st"], "2023-01-02")
        
    def test_library_post_update_valid_end(self):
        """
        Test Library update valid end date
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session["relays"] = TC_RELAYS
        session["libraries"] = TC_LIBRARIES
        session["progress"] = TC_PROGRESS
        session.save()
        response = self.client.get(self.url)
        self.assertEqual(response.context["progress"]["9781444780109"]["en"], "NA")

        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        response = self.client.post(self.url, {"update": "true", "book_info":"e1d342f8901e9db6dcd671b974e130f8bc5353f7-9781444780109", "status":"HR", "stDt":"2023-01-01", "enDt":"2023-01-02"}, follow=True)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        self.assertEqual(response.context["progress"]["9781444780109"]["en"], "2023-01-02")

    def test_library_post_update_hidden(self):
        """
        Test Library update hidden
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = "Y"
        session["relays"] = TC_RELAYS
        session["libraries"] = TC_LIBRARIES
        session["progress"] = TC_PROGRESS
        session.save()

        stDt = datetime.datetime.now().strftime("%Y-%m-%d")

        response = self.client.get(self.url)
        for library in response.context["libraries"]:
            if library["i"] == "fe7046323fc3ccc7c6b2748ba58295fc4206a1a3":
                for book in library["b"]:
                    if book["i"] == "9780007560776":
                        self.assertEqual(book["h"], "N")

        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        response = self.client.post(self.url, {"update": "true", "book_info":"fe7046323fc3ccc7c6b2748ba58295fc4206a1a3-9780007560776", "hidden":"Y"}, follow=True)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        for library in response.context["libraries"]:
            if library["i"] == "fe7046323fc3ccc7c6b2748ba58295fc4206a1a3":
                for book in library["b"]:
                    if book["i"] == "9780007560776":
                        self.assertEqual(book["h"], "Y")
        
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        response = self.client.post(self.url, {"update": "true", "book_info":"fe7046323fc3ccc7c6b2748ba58295fc4206a1a3-9780007560776", "hidden":""}, follow=True)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        for library in response.context["libraries"]:
            if library["i"] == "fe7046323fc3ccc7c6b2748ba58295fc4206a1a3":
                for book in library["b"]:
                    if book["i"] == "9780007560776":
                        self.assertEqual(book["h"], "N")
    
    
    def tearDown(self):
        """
        Tear Down function
        """
        pass