from django.test import TestCase
from nostr_sdk import EventBuilder, Keys, Kind, Tag, TagKind, SingleLetterTag, Alphabet
from utils.Progress import Progress, fetch_progress
import datetime, hashlib
from aioresponses import aioresponses


ISBN = "9780141030586"
ISBN2 = "0140232699"
KEYS = Keys.generate()

class ProgressUnitTests(TestCase):
    def setUp(self):
        pass
    
    def test_progress_parse_event(self):
        """
        Test parsing of progress event
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
        event = EventBuilder(kind=kind, content=content, tags=tags).to_event(keys=KEYS)

        # Parse Valid event (pages)
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

        # Parse Valid event (pct)
        tags = [
            Tag.identifier(hashlib.sha256(ISBN.encode()).hexdigest()),
            Tag.custom(TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.K)),["isbn"]),
            Tag.custom(TagKind.UNKNOWN("unit"), ["pct"]),
            Tag.custom(TagKind.UNKNOWN("current"),["100"]),
            Tag.custom(TagKind.UNKNOWN("max"), ["100"]),
            Tag.custom(TagKind.UNKNOWN("started"), ["2021-01-09"]),
            Tag.custom(TagKind.UNKNOWN("ended"), ["2021-03-10"]),
        ]
        event = EventBuilder(kind=kind, content=content, tags=tags).to_event(keys=KEYS)
        
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

        progress = Progress()
        # Parse None event
        self.assertEqual(progress, progress.parse_event(event=None, isbn=ISBN))
        # Parse Invalid event
        self.assertRaises(ValueError, progress.parse_event, event="Test", isbn=ISBN2)

        # Parse Invalid kind
        kind4 = Kind(30251)
        event4 = EventBuilder(kind=kind4, content=content, tags=tags).to_event(keys=KEYS)
        self.assertRaises(ValueError, progress.parse_event, event=event4, isbn=ISBN)

        # Parse Invalid max/current
        tags = [
            Tag.identifier(hashlib.sha256(ISBN.encode()).hexdigest()),
            Tag.custom(TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.K)),["isbn"]),
            Tag.custom(TagKind.UNKNOWN("unit"), ["pages"]),
            Tag.custom(TagKind.UNKNOWN("current"),["300"]),
            Tag.custom(TagKind.UNKNOWN("max"), ["200"]),
            Tag.custom(TagKind.UNKNOWN("started"), ["2021-01-09"]),
            Tag.custom(TagKind.UNKNOWN("ended"), ["2021-03-10"]),
        ]

        event = EventBuilder(kind=kind, content=content, tags=tags).to_event(keys=KEYS)

        progress = Progress()
        self.assertRaises(ValueError, progress.parse_event, event=event, isbn=ISBN)
    
    def test_progress_parse_dict(self):
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
            ISBN: {
                "id": hashlib.sha256(ISBN.encode()).hexdigest(),
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
        event = progress.bevent.to_event(keys=KEYS)

        self.assertEqual(type(progress.bevent), EventBuilder)
        self.assertEqual(event.kind(), Kind(30250))
        self.assertEqual(event.content(), "")
        tags_list = event.tags()
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
            mocked.get('https://www.googleapis.com/books/v1/volumes?q=isbn:9780141030586', status=200, payload={"items": [{"volumeInfo": {"pageCount": 100}}]})
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
        self.assertEqual(progress.started, None)
        self.assertRaises(ValueError, progress.start_book)

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

    async def test_progress_publish(self):
        """
        Test publishing progress
        """ 
        progress = Progress()
        progress.isbn = ISBN
        progress.identifier = hashlib.sha256(ISBN.encode()).hexdigest()
        progress.external_id = "isbn"
        progress.unit = "pct"
        progress.started = "2021-06-01"
        progress.ended = "2021-06-02"
        progress.progress = "50"
        progress.current = "50"
        progress.max = "100"
        progress.bevent = "Test"

        nsec = KEYS.secret_key().to_bech32()
        nsec_wrong = "nsec123456"
        with self.assertRaises(Exception) as e:
            await progress.publish_event(nsec=None, nym_relays={"wss://relay.damus.io": None})
        self.assertEqual(str(e.exception), "No nsec provided or invalid nsec.")
        with self.assertRaises(Exception) as e:
            await progress.publish_event(nsec=nsec_wrong, nym_relays={"wss://relay.damus.io": None})
        self.assertEqual(str(e.exception), "No nsec provided or invalid nsec.")
        with self.assertRaises(Exception) as e:
            await progress.publish_event(nsec="", nym_relays={"wss://relay.damus.io": None})
        self.assertEqual(str(e.exception), "No nsec provided or invalid nsec.")

        progress = Progress()
        progress.isbn = ISBN
        progress.identifier = hashlib.sha256(ISBN.encode()).hexdigest()
        progress.external_id = "isbn"
        progress.unit = "pct"
        progress.started = "2021-06-01"
        progress.ended = "2021-06-02"
        progress.progress = "50"
        progress.current = "50"
        progress.max = "100"
        progress.bevent = None
        
        with self.assertRaises(Exception) as e:
            await progress.publish_event(nsec=nsec, nym_relays={"wss://relay.damus.io": None})
        self.assertEqual(str(e.exception), "Missing required information.")
        progress.bevent = "Test"
        with self.assertRaises(Exception) as e:
            await progress.publish_event(nsec=nsec, nym_relays=None)
        self.assertEqual(str(e.exception), "Missing required information.")
        with self.assertRaises(Exception) as e:
            await progress.publish_event(nsec=nsec, nym_relays={"wss://relay.damus.io": None})
        self.assertEqual(str(e.exception), "Not a valid builder object.")
        progress.build_event()
        result = await progress.publish_event(nsec=nsec, nym_relays={"wss://relay.damus.io": None})
        self.assertEqual(result, "Published event.")

    async def test_progress_fetch(self):
        """
        Test fetching progress
        """
        nsec = KEYS.secret_key().to_bech32()
        nsec_wrong = "nsec123456"
        npub = KEYS.public_key().to_bech32()
        npub_wrong = "npub123456"
        relays = {"wss://relay.damus.io": None}
        isbns = [ISBN, ISBN2]
        npub_new = Keys.generate().public_key().to_bech32()
        with self.assertRaises(Exception) as e:
            await fetch_progress(isbns=[], npub=npub, relays=relays, nsec=nsec)
        self.assertEqual(str(e.exception), "No ISBNs provided.")
        with self.assertRaises(Exception) as e:
            await fetch_progress(isbns=None, npub=npub, relays=relays, nsec=nsec)
        self.assertEqual(str(e.exception), "No ISBNs provided.")
        with self.assertRaises(Exception) as e:
            await fetch_progress(isbns=["9780141030586"], npub=None, relays=relays, nsec=nsec)
        self.assertEqual(str(e.exception), "No npub provided or invalid npub.")
        with self.assertRaises(Exception) as e:
            await fetch_progress(isbns=["9780141030586"], npub="", relays=relays, nsec=nsec)
        self.assertEqual(str(e.exception), "No npub provided or invalid npub.")
        with self.assertRaises(Exception) as e:
            await fetch_progress(isbns=["9780141030586"], npub="npub123456", relays=relays)
        self.assertEqual(str(e.exception), "No npub provided or invalid npub.")
        with self.assertRaises(Exception) as e:
            await fetch_progress(isbns=["9780141030586"], npub=npub, nsec="", relays=relays)
        self.assertEqual(str(e.exception), "No nsec provided or invalid nsec.")
        with self.assertRaises(Exception) as e:
            await fetch_progress(isbns=["9780141030586"], npub=npub, nsec=nsec_wrong, relays=relays)
        self.assertEqual(str(e.exception), "No nsec provided or invalid nsec.")
        with self.assertRaises(Exception) as e:
            await fetch_progress(isbns=["9780141030586"], npub=npub_new, nsec=nsec, relays=relays)
        self.assertEqual(str(e.exception), "Npub and nsec do not match.")

        result = await fetch_progress(isbns=isbns, npub=npub, nsec=nsec, relays=relays)
        self.assertEqual(result, [])

    def tearDown(self):
        pass