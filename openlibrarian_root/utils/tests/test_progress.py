from django.test import TestCase
from nostr_sdk import EventBuilder, Keys, Kind, Tag, TagKind, SingleLetterTag, Alphabet
from utils.Progress import Progress, fetch_progress
import datetime, hashlib
from aioresponses import aioresponses
from unittest.mock import patch


ISBN = "9780141030586"
ISBN2 = "0140232699"
ISBN3 = "9780007560776"
KEYS = Keys.generate()

class ProgressUnitTests(TestCase):
    def setUp(self):
        pass
    
    def test_progress_parse_event_pages(self):
        """
        Test parsing of progress event (pages)
        """        
        tags = [
            Tag.identifier(hashlib.sha256(ISBN.encode()).hexdigest()),
            Tag.custom(TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.K)),["isbn"]),
            Tag.custom(TagKind.UNKNOWN("unit"), ["pages"]),
            Tag.custom(TagKind.UNKNOWN("current"),["100"]),
            Tag.custom(TagKind.UNKNOWN("max"), ["300"]),
            Tag.custom(TagKind.UNKNOWN("started"), ["2021-01-01"]),
            Tag.custom(TagKind.UNKNOWN("ended"), ["NA"]),
        ]
        kind = Kind(30250)
        content=""
        event = EventBuilder(kind=kind, content=content).tags(tags).sign_with_keys(keys=KEYS)

        progress = Progress()
        progress.parse_event(event=event, isbn=ISBN)

        self.assertEqual(progress.isbn, ISBN)
        self.assertEqual(progress.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(progress.unit, "pages")
        self.assertEqual(progress.current, "100")
        self.assertEqual(progress.max, "300")
        self.assertEqual(progress.started, "2021-01-01")
        self.assertEqual(progress.ended, "NA")
        self.assertEqual(progress.progress, str(round(100/300*100)))
        self.assertEqual(progress.external_id, "isbn")
        self.assertEqual(progress.bevent, None)

    def test_progress_parse_event_pct(self):
        """
        Test parsing of progress event (pct)
        """     
        tags = [
            Tag.identifier(hashlib.sha256(ISBN.encode()).hexdigest()),
            Tag.custom(TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.K)),["isbn"]),
            Tag.custom(TagKind.UNKNOWN("unit"), ["pct"]),
            Tag.custom(TagKind.UNKNOWN("current"),["100"]),
            Tag.custom(TagKind.UNKNOWN("max"), ["100"]),
            Tag.custom(TagKind.UNKNOWN("started"), ["2021-01-09"]),
            Tag.custom(TagKind.UNKNOWN("ended"), ["2021-03-10"]),
        ]
        content=""
        kind = Kind(30250)
        event = EventBuilder(kind=kind, content=content).tags(tags).sign_with_keys(keys=KEYS)

        progress = Progress()
        progress.parse_event(event=event, isbn=ISBN)

        self.assertEqual(progress.isbn, ISBN)
        self.assertEqual(progress.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(progress.unit, "pct")
        self.assertEqual(progress.current, "100")
        self.assertEqual(progress.max, "100")
        self.assertEqual(progress.started, "2021-01-09")
        self.assertEqual(progress.ended, "2021-03-10")
        self.assertEqual(progress.progress, str(round(100/100*100)))
        self.assertEqual(progress.external_id, "isbn")
        self.assertEqual(progress.bevent, None)

    def test_progress_parse_event_none(self):
        """
        Test parsing of progress event (none)
        """    
        progress = Progress()
        self.assertEqual(progress, progress.parse_event(event=None, isbn=ISBN))
    
    def test_progress_parse_event_invalid(self):
        """
        Test parsing of progress event (invalid)
        """    
        progress = Progress()
        self.assertRaises(ValueError, progress.parse_event, event="Test", isbn=ISBN2)

    def test_progress_parse_event_invalid_kind(self):
        """
        Test parsing of progress event (invalid kind)
        """
        tags = [
            Tag.identifier(hashlib.sha256(ISBN.encode()).hexdigest()),
            Tag.custom(TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.K)),["isbn"]),
            Tag.custom(TagKind.UNKNOWN("unit"), ["pct"]),
            Tag.custom(TagKind.UNKNOWN("current"),["100"]),
            Tag.custom(TagKind.UNKNOWN("max"), ["100"]),
            Tag.custom(TagKind.UNKNOWN("started"), ["2021-01-09"]),
            Tag.custom(TagKind.UNKNOWN("ended"), ["2021-03-10"]),
        ]
        kind4 = Kind(30251)
        content=""
        event = EventBuilder(kind=kind4, content=content).tags(tags).sign_with_keys(keys=KEYS)

        progress = Progress()
        self.assertRaises(ValueError, progress.parse_event, event=event, isbn=ISBN)

    def test_progress_parse_event_max_gt_current(self):
        """
        Test parsing of progress event (max > current)
        """   
        tags = [
            Tag.identifier(hashlib.sha256(ISBN.encode()).hexdigest()),
            Tag.custom(TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.K)),["isbn"]),
            Tag.custom(TagKind.UNKNOWN("unit"), ["pages"]),
            Tag.custom(TagKind.UNKNOWN("current"),["200"]),
            Tag.custom(TagKind.UNKNOWN("max"), ["100"]),
            Tag.custom(TagKind.UNKNOWN("started"), ["2021-01-09"]),
            Tag.custom(TagKind.UNKNOWN("ended"), ["2021-03-10"]),
        ]
        kind = Kind(30250)
        content=""
        event = EventBuilder(kind=kind, content=content).tags(tags).sign_with_keys(keys=KEYS)
                
        progress = Progress()
        progress.parse_event(event=event, isbn=ISBN)
        
        self.assertEqual(progress.isbn, ISBN)
        self.assertEqual(progress.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(progress.unit, "pages")
        self.assertEqual(progress.current, "200")
        self.assertEqual(progress.max, "200")  # max is updated to current
        self.assertEqual(progress.started, "2021-01-09")
        self.assertEqual(progress.ended, "2021-03-10")
        self.assertEqual(progress.progress, "100")
        self.assertEqual(progress.external_id, "isbn")
        self.assertEqual(progress.bevent, None)

    def test_progress_parse_event_pct_gt_100(self):
        """
        Test parsing of progress event (max pct > 100)
        """   
        # Test current greater than 100 (pct)
        tags = [
            Tag.identifier(hashlib.sha256(ISBN.encode()).hexdigest()),
            Tag.custom(TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.K)),["isbn"]),
            Tag.custom(TagKind.UNKNOWN("unit"), ["pct"]),
            Tag.custom(TagKind.UNKNOWN("current"),["150"]),
            Tag.custom(TagKind.UNKNOWN("max"), ["100"]),
            Tag.custom(TagKind.UNKNOWN("started"), ["2021-01-09"]),
            Tag.custom(TagKind.UNKNOWN("ended"), ["2021-03-10"]),
        ]
        kind = Kind(30250)
        content=""
        event = EventBuilder(kind=kind, content=content).tags(tags).sign_with_keys(keys=KEYS)
                
        progress = Progress()
        progress.parse_event(event=event, isbn=ISBN)
        
        self.assertEqual(progress.isbn, ISBN)
        self.assertEqual(progress.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(progress.unit, "pct")
        self.assertEqual(progress.current, "100")  # current is capped at 100
        self.assertEqual(progress.max, "100")
        self.assertEqual(progress.started, "2021-01-09")
        self.assertEqual(progress.ended, "2021-03-10")
        self.assertEqual(progress.progress, "100")
        self.assertEqual(progress.external_id, "isbn")
        self.assertEqual(progress.bevent, None)
        
    def test_progress_parse_event_max_0(self):
        """
        Test parsing of progress event (max == 0)
        """   
        tags = [
            Tag.identifier(hashlib.sha256(ISBN.encode()).hexdigest()),
            Tag.custom(TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.K)),["isbn"]),
            Tag.custom(TagKind.UNKNOWN("unit"), ["pages"]),
            Tag.custom(TagKind.UNKNOWN("current"),["0"]),
            Tag.custom(TagKind.UNKNOWN("max"), ["0"]),
            Tag.custom(TagKind.UNKNOWN("started"), ["2021-01-09"]),
            Tag.custom(TagKind.UNKNOWN("ended"), ["2021-03-10"]),
        ]
        kind = Kind(30250)
        content=""
        event = EventBuilder(kind=kind, content=content).tags(tags).sign_with_keys(keys=KEYS)
                
        progress = Progress()
        progress.parse_event(event=event, isbn=ISBN)
        
        self.assertEqual(progress.isbn, ISBN)
        self.assertEqual(progress.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(progress.unit, "pages")
        self.assertEqual(progress.current, "0")
        self.assertEqual(progress.max, "0")
        self.assertEqual(progress.started, "2021-01-09")
        self.assertEqual(progress.ended, "2021-03-10")
        self.assertEqual(progress.progress, "0")
        self.assertEqual(progress.external_id, "isbn")
        self.assertEqual(progress.bevent, None)

    def test_progress_parse_event_current_0(self):
        """
        Test parsing of progress event (current == 0)
        """   
        # Test current is 0 (pages)
        tags = [
            Tag.identifier(hashlib.sha256(ISBN.encode()).hexdigest()),
            Tag.custom(TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.K)),["isbn"]),
            Tag.custom(TagKind.UNKNOWN("unit"), ["pages"]),
            Tag.custom(TagKind.UNKNOWN("current"),["0"]),
            Tag.custom(TagKind.UNKNOWN("max"), ["100"]),
            Tag.custom(TagKind.UNKNOWN("started"), ["2021-01-09"]),
            Tag.custom(TagKind.UNKNOWN("ended"), ["2021-03-10"]),
        ]
        kind = Kind(30250)
        content=""
        event = EventBuilder(kind=kind, content=content).tags(tags).sign_with_keys(keys=KEYS)
                
        progress = Progress()
        progress.parse_event(event=event, isbn=ISBN)
        
        self.assertEqual(progress.isbn, ISBN)
        self.assertEqual(progress.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(progress.unit, "pages")
        self.assertEqual(progress.current, "0")
        self.assertEqual(progress.max, "100")
        self.assertEqual(progress.started, "2021-01-09")
        self.assertEqual(progress.ended, "2021-03-10")
        self.assertEqual(progress.progress, "0")
        self.assertEqual(progress.external_id, "isbn")
        self.assertEqual(progress.bevent, None)
    
    def test_progress_parse_event_missing_fields(self):
        """
        Test parsing of progress event (missing fields)
        """   
        tags = [
        ]
        kind = Kind(30250)
        content=""
        event = EventBuilder(kind=kind, content=content).tags(tags).sign_with_keys(keys=KEYS)
                
        progress = Progress()
        progress.parse_event(event=event, isbn=ISBN)
        
        self.assertEqual(progress.isbn, ISBN)
        self.assertEqual(progress.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(progress.external_id, "isbn")
        self.assertEqual(progress.bevent, None)
        self.assertEqual(progress.unit, "pages")
        self.assertEqual(progress.current, "0")
        self.assertEqual(progress.max, "0")
        self.assertEqual(progress.started, "NA")
        self.assertEqual(progress.ended, "NA")
        self.assertEqual(progress.progress, "0")
    
    def test_progress_parse_event_non_numeric_fields(self):
        """
        Test parsing of progress event (non numeric fields)
        """   
        tags = [
            Tag.identifier(hashlib.sha256(ISBN.encode()).hexdigest()),
            Tag.custom(TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.K)),["isbn"]),
            Tag.custom(TagKind.UNKNOWN("unit"), ["pct"]),
            Tag.custom(TagKind.UNKNOWN("current"),["Apple"]),
            Tag.custom(TagKind.UNKNOWN("max"), ["Bear"]),
            Tag.custom(TagKind.UNKNOWN("started"), ["2021-01-09"]),
            Tag.custom(TagKind.UNKNOWN("ended"), ["2021-03-10"]),
        ]
        kind = Kind(30250)
        content=""
        event = EventBuilder(kind=kind, content=content).tags(tags).sign_with_keys(keys=KEYS)
                
        progress = Progress()
        progress.parse_event(event=event, isbn=ISBN)
        
        self.assertEqual(progress.isbn, ISBN)
        self.assertEqual(progress.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(progress.unit, "pct")
        self.assertEqual(progress.current, "0")
        self.assertEqual(progress.max, "100")
        self.assertEqual(progress.started, "2021-01-09")
        self.assertEqual(progress.ended, "2021-03-10")
        self.assertEqual(progress.progress, "0")
        self.assertEqual(progress.external_id, "isbn")
        self.assertEqual(progress.bevent, None)
    
    def test_progress_parse_event_negative_values(self):
        """
        Test parsing of progress event (negative values)
        """   
        tags = [
            Tag.identifier(hashlib.sha256(ISBN.encode()).hexdigest()),
            Tag.custom(TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.K)),["isbn"]),
            Tag.custom(TagKind.UNKNOWN("unit"), ["pct"]),
            Tag.custom(TagKind.UNKNOWN("current"),["-1"]),
            Tag.custom(TagKind.UNKNOWN("max"), ["-1"]),
            Tag.custom(TagKind.UNKNOWN("started"), ["2021-01-09"]),
            Tag.custom(TagKind.UNKNOWN("ended"), ["2021-03-10"]),
        ]
        kind = Kind(30250)
        content=""
        event = EventBuilder(kind=kind, content=content).tags(tags).sign_with_keys(keys=KEYS)
                
        progress = Progress()
        progress.parse_event(event=event, isbn=ISBN)
        
        self.assertEqual(progress.isbn, ISBN)
        self.assertEqual(progress.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(progress.unit, "pct")
        self.assertEqual(progress.current, "0")
        self.assertEqual(progress.max, "100")
        self.assertEqual(progress.started, "2021-01-09")
        self.assertEqual(progress.ended, "2021-03-10")
        self.assertEqual(progress.progress, "0")
        self.assertEqual(progress.external_id, "isbn")
        self.assertEqual(progress.bevent, None)

    async def test_progress_parse_dict(self):
        """
        Test parsing of progress dict
        """
        data ={
            ISBN2: {
                "id": hashlib.sha256(ISBN2.encode()).hexdigest(),
                "exid": "isbn",
                "unit": "pct",
                "curr": "100",
                "max": "100",
                "st": "2021-06-01",
                "en": "2021-09-02",
                "default": "423",
                "progress" : "100"
            },
        }

        # Parse Valid dict
        progress = Progress()
        progress.parse_dict(data)

        self.assertEqual(progress.isbn, ISBN2)
        self.assertEqual(progress.identifier, hashlib.sha256(ISBN2.encode()).hexdigest())
        self.assertEqual(progress.unit, "pct")
        self.assertEqual(progress.current, "100")
        self.assertEqual(progress.max, "100")
        self.assertEqual(progress.started, "2021-06-01")
        self.assertEqual(progress.ended, "2021-09-02")
        self.assertEqual(progress.progress, "100")
        self.assertEqual(progress.external_id, "isbn")
        self.assertEqual(progress.bevent, None)

        # Parse None / empty dict
        progress = Progress()
        self.assertEqual(progress, progress.parse_dict(data=None))
        self.assertEqual(progress, progress.parse_dict(data={}))

        # Parse Invalid dict
        progress = Progress()
        self.assertRaises(ValueError, progress.parse_dict, data="Test")

        # Test creating new and then parsing
        progress = Progress()
        progress = await progress.new(ISBN2)
        progress.parse_dict(data)

        self.assertEqual(progress.isbn, ISBN2)
        self.assertEqual(progress.identifier, hashlib.sha256(ISBN2.encode()).hexdigest())
        self.assertEqual(progress.unit, "pct")
        self.assertEqual(progress.current, "100")
        self.assertEqual(progress.max, "100")
    
    def test_progress_to_dict(self):
        """
        Test conversion of progress object to dict
        """
        progress = Progress()
        progress.isbn = ISBN
        progress.identifier = hashlib.sha256(ISBN.encode()).hexdigest()
        progress.external_id = "isbn"
        progress.unit = "pct"
        progress.current = "100"
        progress.max = "100"
        progress.started = "2021-06-01"
        progress.ended = "2021-09-02"
        progress.bevent = None
        progress.default_pages = "423"
        progress.progress = "100"

        data = {
            "id": hashlib.sha256(ISBN.encode()).hexdigest(),
            "exid": "isbn",
            "unit": "pct",
            "curr": "100",
            "max": "100",
            "st": "2021-06-01",
            "en": "2021-09-02",
            "default": "423",
            "progress" : "100"
        }

        self.assertEqual(progress.detailed(), data)
    
    def test_progress_build_event(self):
        """
        Test conversion of progress object to event
        """
        progress = Progress()
        progress.isbn = ISBN
        progress.identifier = hashlib.sha256(ISBN.encode()).hexdigest()
        progress.external_id = "isbn"
        progress.unit = "pct"
        progress.current = "100"
        progress.max = "100"
        progress.started = "2021-06-01"
        progress.ended = "2021-09-02"
        progress.bevent = None
        progress.default_pages = "423"
        progress.progress = "100"

        progress = progress.build_event()
        event = progress.bevent.sign_with_keys(keys=KEYS)

        self.assertEqual(type(progress.bevent), EventBuilder)
        self.assertEqual(event.kind(), Kind(30250))
        self.assertEqual(event.content(), "")
        tags_list = event.tags().to_vec()
        for tag in tags_list:
            self.assertEqual(type(tag), Tag)
        
        self.assertEqual(tags_list[0].as_vec()[0], "d")
        self.assertEqual(tags_list[0].as_vec()[1], hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(tags_list[1].as_vec()[0], "k")
        self.assertEqual(tags_list[1].as_vec()[1], "isbn")
        self.assertEqual(tags_list[2].as_vec()[0], "unit")
        self.assertEqual(tags_list[2].as_vec()[1], "pct")
        self.assertEqual(tags_list[3].as_vec()[0], "current")
        self.assertEqual(tags_list[3].as_vec()[1], "100")
        self.assertEqual(tags_list[4].as_vec()[0], "max")
        self.assertEqual(tags_list[4].as_vec()[1], "100")
        self.assertEqual(tags_list[5].as_vec()[0], "started")
        self.assertEqual(tags_list[5].as_vec()[1], "2021-06-01")
        self.assertEqual(tags_list[6].as_vec()[0], "ended")
        self.assertEqual(tags_list[6].as_vec()[1], "2021-09-02")

        # Attempt build event with missing data
        progress = Progress()
        self.assertRaises(ValueError, progress.build_event)
        progress.isbn = ISBN
        self.assertRaises(ValueError, progress.build_event)
        progress.identifier = hashlib.sha256(ISBN.encode()).hexdigest()
        self.assertRaises(ValueError, progress.build_event)
        progress.external_id = "isbn"
        self.assertRaises(ValueError, progress.build_event)
        progress.unit = "pct"
        self.assertRaises(ValueError, progress.build_event)
        progress.current = "100"
        self.assertRaises(ValueError, progress.build_event)
        progress.max = "100"
        self.assertRaises(ValueError, progress.build_event)
        progress.started = "2021-06-01"
        self.assertRaises(ValueError, progress.build_event)
        progress.ended = "2021-09-02"
    
    async def test_progress_new(self):
        """
        Test creation of new progress object
        """
        progress = Progress()
        self.assertEqual(progress.isbn, None)
        self.assertEqual(progress.identifier, None)
        self.assertEqual(progress.external_id, None)
        self.assertEqual(progress.unit, None)
        self.assertEqual(progress.current, None)
        self.assertEqual(progress.max, None)
        self.assertEqual(progress.started, None)
        self.assertEqual(progress.ended, None)
        self.assertEqual(progress.bevent, None)
        self.assertEqual(progress.default_pages, None)

        progress = await progress.new(ISBN)
        self.assertEqual(progress.isbn, ISBN)
        self.assertEqual(progress.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(progress.external_id, "isbn")
        self.assertEqual(progress.unit, "pages")
        self.assertEqual(progress.current, "0")
        self.assertEqual(progress.max, "448")
        self.assertEqual(progress.started, "NA")
        self.assertEqual(progress.ended, "NA")
        self.assertEqual(progress.bevent, None)
        self.assertEqual(progress.default_pages, "448")

        progress = await progress.new(ISBN, default_pages="423")
        self.assertEqual(progress.isbn, ISBN)
        self.assertEqual(progress.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(progress.external_id, "isbn")
        self.assertEqual(progress.unit, "pages")
        self.assertEqual(progress.current, "0")
        self.assertEqual(progress.max, "423")
        self.assertEqual(progress.started, "NA")
        self.assertEqual(progress.ended, "NA")
        self.assertEqual(progress.bevent, None)
        self.assertEqual(progress.default_pages, "423")

        progress = await progress.new(ISBN, default_pages=123)
        self.assertEqual(progress.isbn, ISBN)
        self.assertEqual(progress.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(progress.external_id, "isbn")
        self.assertEqual(progress.unit, "pages")
        self.assertEqual(progress.current, "0")
        self.assertEqual(progress.max, "123")
        self.assertEqual(progress.started, "NA")
        self.assertEqual(progress.ended, "NA")
        self.assertEqual(progress.bevent, None)
        self.assertEqual(progress.default_pages, "123")

        progress = await progress.new(ISBN, default_pages="0")
        self.assertEqual(progress.isbn, ISBN)
        self.assertEqual(progress.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(progress.external_id, "isbn")
        self.assertEqual(progress.unit, "pages")
        self.assertEqual(progress.current, "0")
        self.assertEqual(progress.max, "448")
        self.assertEqual(progress.started, "NA")
        self.assertEqual(progress.ended, "NA")
        self.assertEqual(progress.bevent, None)
        self.assertEqual(progress.default_pages, "448")
    
    async def test_progress_get_default_pages(self):
        """
        Test getting default pages
        """
        progress = Progress()
        with self.assertRaises(ValueError):
            await progress.get_default_pages()

        progress.isbn = ISBN
        await progress.get_default_pages()
        self.assertEqual(progress.default_pages, "448")

        # Test failure of first call
        with aioresponses() as mocked:
            mocked.get('https://openlibrary.org/isbn/9780141030586.json', status=404)
            mocked.get('https://www.googleapis.com/books/v1/volumes?q=isbn:9780141030586', status=200, payload={"items": [{"volumeInfo":{"pageCount": "100"}}]})
            progress = Progress()
            progress.isbn = "9780141030586"
            await progress.get_default_pages()
            self.assertEqual(progress.default_pages, "100")

        # Test failure of both calls
        with aioresponses() as mocked:
            mocked.get('https://openlibrary.org/isbn/9780141030586.json', status=404)
            mocked.get('https://www.googleapis.com/books/v1/volumes?q=isbn:9780141030586', status=404)
            progress = Progress()
            progress.isbn = "9780141030586"
            await progress.get_default_pages()
            self.assertEqual(progress.default_pages, "NOT AVAILABLE")
    
    def test_progress_start_book(self):
        """
        Test starting a book
        """
        progress = Progress()
        progress.isbn = ISBN
        self.assertEqual(progress.started, None)
        progress.start_book()
        self.assertEqual(progress.started, datetime.datetime.now().strftime("%Y-%m-%d"))

        progress = Progress()
        progress.isbn = ISBN
        progress.ended = "2021-06-01"
        progress.current = "100"
        progress.progress = "100"
        progress.max = "100"
        self.assertEqual(progress.started, None)
        progress.start_book()
        self.assertEqual(progress.started, datetime.datetime.now().strftime("%Y-%m-%d"))
        self.assertEqual(progress.ended, "NA")
        self.assertEqual(progress.current, "0")
        self.assertEqual(progress.progress, "0")
        self.assertEqual(progress.max, "100")

        progress = Progress()
        progress.isbn = ISBN
        self.assertEqual(progress.started, None)
        progress.started = "2021-06-01"
        progress.start_book(started="2021-10-01")
        self.assertEqual(progress.started, "2021-10-01")
    
    async def test_progress_end_book(self):
        """
        Test ending a book
        """
        progress = Progress()
        progress.isbn = ISBN
        self.assertEqual(progress.ended, None)
        self.assertRaises(ValueError, progress.end_book)

        progress = Progress()
        progress.isbn = ISBN
        progress.started = "2021-06-01"
        progress.end_book()
        self.assertEqual(progress.ended, datetime.datetime.now().strftime("%Y-%m-%d"))

        progress = Progress()
        progress.isbn = ISBN
        progress.started = "2021-06-01"
        progress.ended = "2021-10-01"
        progress.end_book(ended="2021-06-02")
        self.assertEqual(progress.ended, "2021-06-02")

        progress = Progress()
        progress.isbn = ISBN
        progress.unit = "pct"
        progress.started = "2021-06-01"
        progress.end_book()
        self.assertEqual(progress.ended, datetime.datetime.now().strftime("%Y-%m-%d"))
        self.assertEqual(progress.progress, "100")
        self.assertEqual(progress.current, "100")
        self.assertEqual(progress.max, "100")

        progress = Progress()
        progress.isbn = ISBN
        progress.unit = "pages"
        progress.started = "2021-06-01"
        progress.end_book(ended="2021-06-02")
        self.assertEqual(progress.ended, "2021-06-02")
        self.assertEqual(progress.progress, "100")
        self.assertEqual(progress.current, None)
        self.assertEqual(progress.max, None)
        
        progress = Progress()
        progress.isbn = ISBN
        progress.unit = "pages"
        progress.started = "2021-06-01"
        progress.max = "448"
        progress.end_book(ended="2021-06-02")
        self.assertEqual(progress.ended, "2021-06-02")
        self.assertEqual(progress.progress, "100")
        self.assertEqual(progress.current, "448")
        self.assertEqual(progress.max, "448")

        progress = Progress()
        await progress.new(isbn=ISBN)
        progress.unit = "pages"
        progress.started = "2021-06-01"
        progress.max = None
        progress.end_book(ended="2021-06-02")
        self.assertEqual(progress.ended, "2021-06-02")
        self.assertEqual(progress.progress, "100")
        self.assertEqual(progress.current, "448")
        self.assertEqual(progress.max, "448")
        self.assertEqual(progress.default_pages, "448")

    def test_progress_update(self):
        """
        Test updating progress
        """
        progress = Progress()
        progress.isbn = ISBN
        self.assertEqual(progress.current, None)
        self.assertRaises(ValueError, progress.update_progress, current=None)
        self.assertRaises(ValueError, progress.update_progress, current="100", unit="new")
        
        progress = Progress()
        progress.isbn = ISBN
        progress.unit = "pages"
        progress.default_pages = "423"
        self.assertEqual(progress.started, None)
        self.assertEqual(progress.current, None)
        self.assertEqual(progress.unit, "pages")
        progress.update_progress(current="50",unit="pct")
        self.assertEqual(progress.current, "50")
        self.assertEqual(progress.unit, "pct")
        self.assertEqual(progress.progress, "50")
        self.assertEqual(progress.default_pages, "423")
        self.assertEqual(progress.max, "100")

        progress = Progress()
        progress.isbn = ISBN
        progress.unit = "pages"
        progress.default_pages = "423"
        progress.update_progress(current="50", max="300")
        self.assertEqual(progress.current, "50")
        self.assertEqual(progress.unit, "pages")
        self.assertEqual(progress.progress, "17")
        self.assertEqual(progress.default_pages, "423")
        self.assertEqual(progress.max, "300")

        progress = Progress()
        progress.isbn = ISBN
        progress.unit = "pages"
        progress.default_pages = "423"
        self.assertRaises(ValueError, progress.update_progress, current="300", max="50")

        progress = Progress()
        progress.isbn = ISBN
        progress.unit = "pct"
        progress.default_pages = "423"
        progress.update_progress(current="50", unit="pages")
        self.assertEqual(progress.current, "50")
        self.assertEqual(progress.unit, "pages")
        self.assertEqual(progress.progress, "12")
        self.assertEqual(progress.default_pages, "423")
        self.assertEqual(progress.max, "423")

        progress = Progress()
        progress.isbn = ISBN
        progress.unit = "pages"
        progress.default_pages = "423"
        progress.update_progress(current="50")
        self.assertEqual(progress.current, "50")
        self.assertEqual(progress.unit, "pages")
        self.assertEqual(progress.progress, "12")
        self.assertEqual(progress.default_pages, "423")
        self.assertEqual(progress.max, "423")

    async def test_progress_fetch_empty(self):
        """
        Test fetching progress (empty)
        """
        npub = KEYS.public_key().to_bech32()
        relays = {"wss://relay.damus.io": None}
        isbns = [ISBN, ISBN2]
        result = await fetch_progress(isbns=[], npub=npub, relays=relays)
        self.assertEqual(result, {})
        with self.assertRaises(Exception) as e:
            await fetch_progress(isbns=None, npub=npub, relays=relays)
        self.assertEqual(str(e.exception), "No ISBNs provided.")
        with self.assertRaises(Exception) as e:
            await fetch_progress(isbns=["9780141030586"], npub=None, relays=relays)
        self.assertEqual(str(e.exception), "No npub provided or invalid npub.")
        with self.assertRaises(Exception) as e:
            await fetch_progress(isbns=["9780141030586"], npub="", relays=relays)
        self.assertEqual(str(e.exception), "No npub provided or invalid npub.")
        with self.assertRaises(Exception) as e:
            await fetch_progress(isbns=["9780141030586"], npub="npub123456", relays=relays)
        self.assertEqual(str(e.exception), "No npub provided or invalid npub.")

        # For empty list create new objects
        result = await fetch_progress(isbns=isbns, npub=npub, relays=relays)
        new_list = [await Progress().new(isbn=isbn) for isbn in isbns]
        detailed_dict = {progress.isbn: progress.detailed() for progress in new_list}
        self.assertEqual(result, detailed_dict)

    @patch('utils.Progress.nostr_get')
    async def test_progress_fetch_patch(self, mock_nostr_get):
        """
        Test fetching progress (patch)
        """

        # Mock events
        tags = [
            Tag.identifier(hashlib.sha256(ISBN.encode()).hexdigest()),
            Tag.custom(TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.K)),["isbn"]),
            Tag.custom(TagKind.UNKNOWN("unit"), ["pages"]),
            Tag.custom(TagKind.UNKNOWN("current"),["100"]),
            Tag.custom(TagKind.UNKNOWN("max"), ["300"]),
            Tag.custom(TagKind.UNKNOWN("started"), ["2021-01-01"]),
            Tag.custom(TagKind.UNKNOWN("ended"), ["NA"]),
        ]
        kind = Kind(30250)
        content=""
        event1 = EventBuilder(kind=kind, content=content).tags(tags).sign_with_keys(keys=KEYS)
        
        tags = [
            Tag.identifier(hashlib.sha256(ISBN2.encode()).hexdigest()),
            Tag.custom(TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.K)),["isbn"]),
            Tag.custom(TagKind.UNKNOWN("unit"), ["pct"]),
            Tag.custom(TagKind.UNKNOWN("current"),["50"]),
            Tag.custom(TagKind.UNKNOWN("max"), ["100"]),
            Tag.custom(TagKind.UNKNOWN("started"), ["2021-06-01"]),
            Tag.custom(TagKind.UNKNOWN("ended"), ["2021-06-02"]),
        ]

        event2 = EventBuilder(kind=kind, content=content).tags(tags).sign_with_keys(keys=KEYS)
        events = [event1, event2]

        mock_nostr_get.return_value = {"progress": events}
        actual = await fetch_progress(isbns=[ISBN, ISBN2, ISBN3], npub=KEYS.public_key().to_bech32(), relays={"wss://relay.damus.io": None})

        parsed1 = await Progress().parse_event(event=event1, isbn=ISBN).get_default_pages()
        parsed2 = await Progress().parse_event(event=event2, isbn=ISBN2).get_default_pages()
        new = await Progress().new(isbn=ISBN3)
        new = await new.get_default_pages()

        expected = {ISBN: parsed1.detailed(), ISBN2: parsed2.detailed(), ISBN3: new.detailed()}
        self.assertEqual(actual, expected)

    def tearDown(self):
        pass