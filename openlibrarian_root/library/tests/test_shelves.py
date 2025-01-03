from django.test import TestCase, Client
from almanac.tests.test_settings import SettingsUnitTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import datetime, io, sys
from hashlib import sha256

TC_LIBRARIES = [
    {'s': 'TRS', 'i': 'aea571dbde5eb6ebec93c91b95486539b9491962', 't': 'To Read (S)', 'd': 'Books on the shelf ready to read', 'c': 'Books & Literature (OpenLibrarian)', 'b': [{'t': 'The Olive Farm', 'a': 'Carol Drinkwater', 'i': '0349114749', 'c': 'https://covers.openlibrary.org/b/isbn/0349114749-M.jpg', 'h': 'N'}, {'t': 'Beauty', 'a': 'Sheri S. Tepper', 'i': '1857987225', 'c': 'https://covers.openlibrary.org/b/isbn/1857987225-M.jpg', 'h': 'N'}, {'t': 'Angry Aztecs', 'a': 'Terry Deary', 'i': '9781407104256', 'c': 'https://covers.openlibrary.org/b/isbn/9781407104256-M.jpg', 'h': 'N'}, {'t': 'March', 'a': 'Geraldine Brooks', 'i': '0007165870', 'c': 'https://covers.openlibrary.org/b/isbn/0007165870-M.jpg', 'h': 'N'}]},
    {'s': 'TRW', 'i': 'f76a2d0c13b20a32eeefc4e4f5b393f7b0d6dccc', 't': 'To Read (W)', 'd': "Books I want to read but don't own yet", 'c': 'Books & Literature (OpenLibrarian)', 'b': [{'t': 'Tomorrow', 'a': 'Unknown Author', 'i': '9780718183899', 'c': 'https://covers.openlibrary.org/b/isbn/9780718183899-M.jpg', 'h': 'Y'}, {'t': 'Flesh House', 'a': 'Stuart MacBride', 'i': '9780007244546', 'c': 'https://covers.openlibrary.org/b/isbn/9780007244546-M.jpg', 'h': 'Y'}]},
    {'s': 'CR', 'i': 'fe7046323fc3ccc7c6b2748ba58295fc4206a1a3', 't': 'Currently Reading', 'd': 'Books I am currently reading', 'c': 'Books & Literature (OpenLibrarian)', 'b': [{'t': 'MANDIBLES A FAMILY 2029-47_PB', 'a': 'SHRIVER  LIONEL', 'i': '9780007560776', 'c': 'https://covers.openlibrary.org/b/isbn/9780007560776-M.jpg', 'h': 'N'}]},
    {'s': 'HR', 'i': 'e1d342f8901e9db6dcd671b974e130f8bc5353f7', 't': 'Have Read', 'd': 'Books I have finished reading', 'c': 'Books & Literature (OpenLibrarian)', 'b': [{'t': "Walker's Guide to Outdoor Clues and Signs", 'a': 'Tristan Gooley', 'i': '9781444780109', 'c': 'https://covers.openlibrary.org/b/isbn/9781444780109-M.jpg', 'h': 'Y'}, {'t': 'Humankind', 'a': 'Rutger Bregman', 'i': '9781408898956', 'c': 'https://covers.openlibrary.org/b/isbn/9781408898956-M.jpg', 'h': 'Y'}, {'t': 'Hackers', 'a': 'Steven Levy', 'i': '0140232699', 'c': 'https://covers.openlibrary.org/b/isbn/0140232699-M.jpg', 'h': 'Y'}]}
]

TC_PROGRESS = {
    "9780007560776" : {
    "id": sha256("9780007560776".encode()).hexdigest(),
    "exid": "isbn",
    "unit": "pct","curr": "0",
    "max": "100",
    "st": "NA",
    "en": "NA",
    "default": "NOT AVAILABLE",
    "progress": "0"},
    "9781444780109" : {
    "id": sha256("9781444780109".encode()).hexdigest(),
    "exid": "isbn",
    "unit": "pct",
    "curr": "100",
    "max": "100",
    "st": "NA",
    "en": "NA",
    "default": "NOT AVAILABLE",
    "progress": "0"},
    "9781408898956" : {
    "id": sha256("9781408898956".encode()).hexdigest(),
    "exid": "isbn",
    "unit": "pct",
    "curr": "100",
    "max": "100",
    "st": "NA",
    "en": "NA",
    "default": "NOT AVAILABLE",
    "progress": "0"},
    "0140232699" : {
    "id": sha256("0140232699".encode()).hexdigest(),
    "exid": "isbn",
    "unit": "pct",
    "curr": "100",
    "max": "100",
    "st": "NA",
    "en": "NA",
    "default": "NOT AVAILABLE",
    "progress": "0"}
}

TC_NPUB = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
TC_NSEC = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
TC_RELAYS = {"wss://relay.damus.io": None}


class ShelvesFunctionalTestCase(TestCase):
    """
    Functional Tests for the relays page
    """
    def setUp(self):
        """
        Set Up and instantiate driver
        """
        self.url = "/library/shelves/"
        self.driver = webdriver.Firefox()
        self.driver.get(f"http://127.0.0.1:8000/login-npub/")
        self.driver.find_element(by=By.ID, value="npub").send_keys("npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n")
        self.driver.find_element(by=By.ID, value="submit").click()
        sleep(1)

    def test_shelves_back(self):
        """
        Test Relays Back Button
        """
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
    Unit Tests for the settings page
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
        session["nsec"] = TC_NSEC
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
        session["nsec"] = TC_NSEC
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
        session["nsec"] = TC_NSEC
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
        session["nsec"] = TC_NSEC
        session["relays"] = TC_RELAYS
        session.save()
        response = self.client.post(self.url, {"refresh": "refresh"})
        self.assertIn("progress", response.context)
        self.assertIn("libraries", response.context)
        self.assertEqual(4, len(response.context["libraries"]))
        self.assertEqual(response.context["notification"], None)
    
    def test_library_fetch_none(self):
        """
        Test Library Fetch (none libs) logged in
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = TC_NSEC
        session["relays"] = TC_RELAYS
        session["libraries"] = None
        session.save()
        response = self.client.get(self.url)
        self.assertIn("progress", response.context)
        self.assertIn("libraries", response.context)
        self.assertEqual(4, len(response.context["libraries"]))
        self.assertEqual(response.context["notification"], None)
    
    def test_library_fetch_miss(self):
        """
        Test Library Fetch (missing libs) logged in
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = TC_NSEC
        session["relays"] = TC_RELAYS
        session.save()
        response = self.client.get(self.url)
        self.assertIn("progress", response.context)
        self.assertIn("libraries", response.context)
        self.assertEqual(4, len(response.context["libraries"]))
        self.assertEqual(response.context["notification"], None)
    
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
        response = self.client.post(self.url, {"refresh": "refresh"})
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
        session["nsec"] = TC_NSEC
        session["relays"] = TC_RELAYS
        session["libraries"] = TC_LIBRARIES
        session.save()
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        response = self.client.post(self.url, {"remove_book": "true", "book_info":"fe7046323fc3ccc7c6b2748ba58295fc4206a1a3-9780007560776"})
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        for library in response.context["libraries"]:
            if library["i"] == "fe7046323fc3ccc7c6b2748ba58295fc4206a1a3":
                for book in library["b"]:
                    self.assertNotEqual("9780007560776", book["i"])
                break
        
        # Review Event string for library update
        event_str1 = output.split("\n")[2]
        self.assertIn(f'tags":[["d","fe7046323fc3ccc7c6b2748ba58295fc4206a1a3"],["title","Currently Reading"],["description","Books I am currently reading"]]', event_str1)
        self.assertIn('"content":"Books & Literature (OpenLibrarian):', event_str1)
        self.assertIn('"kind":30003', event_str1)
    
    def test_library_post_moved_to_cr_from_trw(self):
        """
        Test Library move book to CR shelf from TRW
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = TC_NSEC
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
        self.assertEqual(response.context["progress"]["9780718183899"]["max"], "NOT AVAILABLE")
        self.assertEqual(response.context["progress"]["9780718183899"]["st"], stDt)
        self.assertEqual(response.context["progress"]["9780718183899"]["en"], "NA")
        self.assertEqual(response.context["progress"]["9780718183899"]["unit"], "pages")
        self.assertEqual(response.context["progress"]["9780718183899"]["progress"], "0")
        self.assertEqual(response.context["progress"]["9780718183899"]["default"], "NOT AVAILABLE")
        for book in old_lib["b"]:
            self.assertNotEqual("9780718183899", book["i"])
        
    def test_library_post_moved_to_hr_from_trw(self):
        """
        Test Library move book to HR shelf TRW
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = TC_NSEC
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
        self.assertEqual(response.context["progress"]["9780718183899"]["curr"], "NOT AVAILABLE")
        self.assertEqual(response.context["progress"]["9780718183899"]["max"], "NOT AVAILABLE")
        self.assertEqual(response.context["progress"]["9780718183899"]["st"], stDt)
        self.assertEqual(response.context["progress"]["9780718183899"]["en"], enDt)
        self.assertEqual(response.context["progress"]["9780718183899"]["unit"], "pages")
        self.assertEqual(response.context["progress"]["9780718183899"]["progress"], "100")
        self.assertEqual(response.context["progress"]["9780718183899"]["default"], "NOT AVAILABLE")
        for book in old_lib["b"]:
            self.assertNotEqual("9780718183899", book["i"])
        
        # Review Event string for progress update
        event_str1 = output.split("\n")[2]
        self.assertIn(f'"tags":[["d","57e52842eaf12f8fc151bb67b09c4f4ff36d5a3a882591ee6ad988e769d94134"],["k","isbn"],["unit","pages"],["current","NOT AVAILABLE"],["max","NOT AVAILABLE"],["started","{stDt}"],["ended","{enDt}"]]', event_str1)
        self.assertIn('"content":""', event_str1)
        self.assertIn('"kind":30250', event_str1)

        # Review Event string for library update (HR)
        event_str3 = output.split("\n")[6]
        self.assertIn('"tags":[["d","e1d342f8901e9db6dcd671b974e130f8bc5353f7"],["title","Have Read"],["description","Books I have finished reading"]]', event_str3)
        self.assertIn('"content":"Books & Literature (OpenLibrarian):', event_str3)
        self.assertIn('"kind":30003', event_str3)

        # Review Event string for library update (TRW)
        event_str4 = output.split("\n")[10]
        self.assertIn(""" "tags":[["d","f76a2d0c13b20a32eeefc4e4f5b393f7b0d6dccc"],["title","To Read (W)"],["description","Books I want to read but don't own yet"]] """.strip(), event_str4)
        self.assertIn('"content":"Books & Literature (OpenLibrarian):', event_str4)
        self.assertIn('"kind":30003', event_str4)
    
    def test_library_post_moved_to_trs_from_trw(self):
        """
        Test Library move book to TRS shelf TRW
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = TC_NSEC
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

        # Review Event string for library update (TRS)
        event_str1 = output.split("\n")[2]
        self.assertIn(f'"tags":[["d","aea571dbde5eb6ebec93c91b95486539b9491962"],["title","To Read (S)"],["description","Books on the shelf ready to read"],["i","isbn:0349114749"],["i","isbn:1857987225"],["i","isbn:9781407104256"],["i","isbn:0007165870"]]', event_str1)
        self.assertIn('"content":"Books & Literature (OpenLibrarian):', event_str1)
        self.assertIn('"kind":30003', event_str1)

        # Review Event string for library update (TRW)
        event_str2 = output.split("\n")[6]
        self.assertIn(""" "tags":[["d","f76a2d0c13b20a32eeefc4e4f5b393f7b0d6dccc"],["title","To Read (W)"],["description","Books I want to read but don't own yet"]] """.strip(), event_str2)
        self.assertIn('"content":"Books & Literature (OpenLibrarian):', event_str2)
        self.assertIn('"kind":30003', event_str2)
   
    def test_library_post_move_from_cr_to_hr(self):
        """
        Test Library move book from CR to HR
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = TC_NSEC
        session["relays"] = TC_RELAYS
        session["libraries"] = TC_LIBRARIES
        session["progress"] = TC_PROGRESS
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

        # Review Event string for progress update
        event_str1 = output.split("\n")[2]
        self.assertIn(f'"tags":[["d","de3dc5edc60f4bcaf5f7e1070fcbde72241c846893085af271447dc0bd619764"],["k","isbn"],["unit","pct"],["current","100"],["max","100"],["started","{stDt}"],["ended","{enDt}"]]', event_str1)
        self.assertIn('"content":""', event_str1)
        self.assertIn('"kind":30250', event_str1)

        # Review Event string for notification update
        event_str2 = output.split("\n")[6]
        self.assertIn('"tags":[["t","Read"],["t","Books"],["t","Reading"],["t","OpenLibrarian"],["t","OpenLibrary"],["t","Bookstr"],["t","Readstr"]]', event_str2)
        self.assertIn('"content":"I just finished reading ', event_str2)
        self.assertIn('and gave it 4 out of 5 stars! ', event_str2)
        self.assertIn('"kind":1', event_str2)

        # Review Event string for library update (HR)
        event_str3 = output.split("\n")[10]
        self.assertIn('"tags":[["d","e1d342f8901e9db6dcd671b974e130f8bc5353f7"],["title","Have Read"],["description","Books I have finished reading"],["i","isbn:9780007560776"]]', event_str3)
        self.assertIn('"content":"Books & Literature (OpenLibrarian):', event_str3)
        self.assertIn('"kind":30003', event_str3)

        # Review Event string for library update (CR)
        event_str4 = output.split("\n")[14]
        self.assertIn('"tags":[["d","fe7046323fc3ccc7c6b2748ba58295fc4206a1a3"],["title","Currently Reading"],["description","Books I am currently reading"]]', event_str4)
        self.assertIn('"content":"Books & Literature (OpenLibrarian):', event_str4)
        self.assertIn('"kind":30003', event_str4)

    def test_library_post_move_from_hr_to_cr(self):
        """
        Test Library move book from HR to CR
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = TC_NSEC
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
        self.assertEqual(response.context["progress"]["9781444780109"]["curr"], "100")
        self.assertEqual(response.context["progress"]["9781444780109"]["max"], "100")
        self.assertEqual(response.context["progress"]["9781444780109"]["st"], stDt)
        self.assertEqual(response.context["progress"]["9781444780109"]["en"], "NA")
        self.assertEqual(response.context["progress"]["9781444780109"]["unit"], "pct")
        self.assertEqual(response.context["progress"]["9781444780109"]["progress"], "0")
        self.assertEqual(response.context["progress"]["9781444780109"]["default"], "NOT AVAILABLE")
        for book in old_lib["b"]:
            self.assertNotEqual("9781444780109", book["i"])

        # Review Event string for progress update
        event_str1 = output.split("\n")[2]
        self.assertIn(f'"tags":[["d","a479b971d0d1e054dae477e8eed7a4897ef62e86de547de73c98ca6b05261783"],["k","isbn"],["unit","pct"],["current","100"],["max","100"],["started","{stDt}"],["ended","NA"]]', event_str1)
        self.assertIn('"content":""', event_str1)
        self.assertIn('"kind":30250', event_str1)

        # Review Event string for notification update
        event_str2 = output.split("\n")[6]
        self.assertIn('"tags":[["t","Read"],["t","Books"],["t","Reading"],["t","OpenLibrarian"],["t","OpenLibrary"],["t","Bookstr"],["t","Readstr"]]', event_str2)
        self.assertIn('"content":"I just started reading ', event_str2)
        self.assertIn('"kind":1', event_str2)

        # Review Event string for library update (HR)
        event_str3 = output.split("\n")[10]
        self.assertIn('"tags":[["d","fe7046323fc3ccc7c6b2748ba58295fc4206a1a3"],["title","Currently Reading"],["description","Books I am currently reading"],["i","isbn:9780007560776"]]', event_str3)
        self.assertIn('"content":"Books & Literature (OpenLibrarian):', event_str3)
        self.assertIn('"kind":30003', event_str3)

        # Review Event string for library update (CR)
        event_str4 = output.split("\n")[14]
        self.assertIn('"tags":[["d","e1d342f8901e9db6dcd671b974e130f8bc5353f7"],["title","Have Read"],["description","Books I have finished reading"]]', event_str4)
        self.assertIn('"content":"Books & Literature (OpenLibrarian):', event_str4)
        self.assertIn('"kind":30003', event_str4)
    
    def test_library_post_update_invalid_dates(self):
        """
        Test Library update invalid dates
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = TC_NSEC
        session["relays"] = TC_RELAYS
        session["libraries"] = TC_LIBRARIES
        session["progress"] = TC_PROGRESS
        session.save()
        response = self.client.post(self.url, {"update": "true", "book_info":"f76a2d0c13b20a32eeefc4e4f5b393f7b0d6dccc-9780718183899", "stDt":"2023-01-02", "enDt":"2023-01-01"})
        self.assertEqual("End date is before start date.", response.context["notification"])

        response = self.client.post(self.url, {"update": "true", "book_info":"f76a2d0c13b20a32eeefc4e4f5b393f7b0d6dccc-9780718183899", "stDt":"NA", "enDt":"2023-01-01"})
        self.assertEqual("Start date is required when adding end date.", response.context["notification"])

    def test_library_post_update_invalid_progress(self):    
        """
        Test Library update invalid progress
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = TC_NSEC
        session["relays"] = TC_RELAYS
        session["libraries"] = TC_LIBRARIES
        session["progress"] = TC_PROGRESS
        session.save()
        response = self.client.post(self.url, {"update": "true", "book_info":"f76a2d0c13b20a32eeefc4e4f5b393f7b0d6dccc-9780718183899", "unitRadio":"pages", "maxPage":"100", "currentPage":"101"})
        self.assertEqual("Current progress is greater than max.", response.context["notification"])

    def test_library_post_update_valid_unit(self):
        """
        Test Library update valid unit
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = TC_NSEC
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

        # Review Event string for progress update
        event_str1 = output.split("\n")[2]
        self.assertIn(f'"tags":[["d","de3dc5edc60f4bcaf5f7e1070fcbde72241c846893085af271447dc0bd619764"],["k","isbn"],["unit","pages"],["current","50"],["max","100"],["started","{stDt}"],["ended","NA"]]', event_str1)
        self.assertIn('"content":""', event_str1)
        self.assertIn('"kind":30250', event_str1)

        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        response = self.client.post(self.url, {"update": "true", "book_info":"fe7046323fc3ccc7c6b2748ba58295fc4206a1a3-9780007560776", "unitRadio":"pct", "maxPct":"100", "currentPct":"50"}, follow=True)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        self.assertEqual(response.context["progress"]["9780007560776"]["unit"], "pct")

        # Review Event string for progress update
        event_str2 = output.split("\n")[2]
        self.assertIn(f'"tags":[["d","de3dc5edc60f4bcaf5f7e1070fcbde72241c846893085af271447dc0bd619764"],["k","isbn"],["unit","pct"],["current","50"],["max","100"],["started","{stDt}"],["ended","NA"]]', event_str2)
        self.assertIn('"content":""', event_str2)
        self.assertIn('"kind":30250', event_str2)

    def test_library_post_update_valid_start(self):
        """
        Test Library update valid start date
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = TC_NSEC
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
        
        # Review Event string for progress update
        event_str1 = output.split("\n")[3]
        self.assertIn('"tags":[["d","de3dc5edc60f4bcaf5f7e1070fcbde72241c846893085af271447dc0bd619764"],["k","isbn"],["unit","pct"],["current","0"],["max","100"],["started","2023-01-02"],["ended","NA"]]', event_str1)
        self.assertIn('"content":""', event_str1)
        self.assertIn('"kind":30250', event_str1)

    def test_library_post_update_valid_end(self):
        """
        Test Library update valid end date
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = TC_NSEC
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
        
        # Review Event string for library update (HR)
        event_str1 = output.split("\n")[2]
        self.assertIn('"tags":[["d","e1d342f8901e9db6dcd671b974e130f8bc5353f7"],["title","Have Read"],["description","Books I have finished reading"],["i","isbn:9781444780109"]]', event_str1)
        self.assertIn('"content":"Books & Literature (OpenLibrarian):', event_str1)
        self.assertIn('"kind":30003', event_str1)

        # Review Event string for progress update
        event_str2 = output.split("\n")[6]
        self.assertIn(f'"tags":[["d","a479b971d0d1e054dae477e8eed7a4897ef62e86de547de73c98ca6b05261783"],["k","isbn"],["unit","pct"],["current","100"],["max","100"],["started","2023-01-01"],["ended","2023-01-02"]]', event_str2)
        self.assertIn('"content":""', event_str2)
        self.assertIn('"kind":30250', event_str2)

    def test_library_post_update_hidden(self):
        """
        Test Library update hidden
        """
        session = self.client.session
        session["npub"] = TC_NPUB
        session["nsec"] = TC_NSEC
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
        
        # Review Event string for library update
        event_str1 = output.split("\n")[2]
        self.assertIn(f'"tags":[["d","fe7046323fc3ccc7c6b2748ba58295fc4206a1a3"],["title","Currently Reading"],["description","Books I am currently reading"]]', event_str1)
        self.assertIn('"content":"Books & Literature (OpenLibrarian):1', event_str1)
        self.assertIn('"kind":30003', event_str1)

        # Review Event string for progress update
        event_str2 = output.split("\n")[7]
        self.assertIn(f'"tags":[["d","de3dc5edc60f4bcaf5f7e1070fcbde72241c846893085af271447dc0bd619764"],["k","isbn"],["unit","pct"],["current","0"],["max","100"],["started","{stDt}"],["ended","NA"]]', event_str2)
        self.assertIn('"content":""', event_str2)
        self.assertIn('"kind":30250', event_str2)

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
        
        # Review Event string for library update
        event_str1 = output.split("\n")[2]
        self.assertIn(f'"tags":[["d","fe7046323fc3ccc7c6b2748ba58295fc4206a1a3"],["title","Currently Reading"],["description","Books I am currently reading"],["i","isbn:9780007560776"]]', event_str1)
        self.assertIn('"content":"Books & Literature (OpenLibrarian):0', event_str1)
        self.assertIn('"kind":30003', event_str1)
        
        

    def tearDown(self):
        """
        Tear Down function
        """
        pass