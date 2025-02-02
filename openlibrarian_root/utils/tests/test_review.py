from django.test import TestCase
from nostr_sdk import EventBuilder, Keys, Kind, Tag, TagKind, SingleLetterTag, Alphabet
import hashlib
from unittest.mock import patch
from utils.Review import Review, fetch_reviews

KEYS = Keys.generate()
ISBN = "9780141030586"
ISBN2 = "0140232699"
ISBN3 = "9780007560776"

class ReviewUnitTests(TestCase):
    def setUp(self):
        pass

    def test_review(self):
        """
        Test Review (basic instantiation)
        """
        review = Review()
        self.assertEqual(review.isbn, None)
        self.assertEqual(review.identifier, None)
        self.assertEqual(review.external_id, None)
        self.assertEqual(review.rating_normal, None)
        self.assertEqual(review.rating_raw, None)
        self.assertEqual(review.rating, None)
        self.assertEqual(review.content, None)
        self.assertEqual(review.tags, None)
        self.assertEqual(review.bevent, None)

    async def test_review_new(self):
        """
        Test Review (new)
        """
        review = Review()
        await review.new(ISBN)
        self.assertEqual(review.isbn, ISBN)
        self.assertEqual(review.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(review.external_id, "isbn")
        self.assertEqual(review.rating_normal, "NA")
        self.assertEqual(review.rating_raw, "NA")
        self.assertEqual(review.rating, None)
        self.assertEqual(review.content, "NA")
        self.assertEqual(review.tags, [])
        self.assertEqual(review.bevent, None)

    async def test_review_review(self):
        """
        Test Review (review)
        """
        review = Review()
        await review.review(ISBN, 3.5, "This is a review", ["tag1", "tag2"])
        self.assertEqual(review.isbn, ISBN)
        self.assertEqual(review.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(review.external_id, "isbn")
        self.assertEqual(review.rating_normal, "0.7")
        self.assertEqual(review.rating_raw, "3.5/5")
        self.assertEqual(review.rating, 3.5)
        self.assertEqual(review.content, "This is a review")
        self.assertEqual(review.tags, ["tag1", "tag2"])
        self.assertEqual(review.bevent, None)


    async def test_review_review_invalid(self):
        """
        Test Review (review invalid)
        """
        # Test review with rating not an float
        review = Review()
        await review.review(ISBN, "not an float", "This is a review", ["tag1", "tag2"])
        self.assertEqual(review.isbn, ISBN)
        self.assertEqual(review.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(review.external_id, "isbn")
        self.assertEqual(review.rating_normal, "NA")
        self.assertEqual(review.rating_raw, "NA")
        self.assertEqual(review.rating, None)
        self.assertEqual(review.content, "NA")
        self.assertEqual(review.tags, [])
        self.assertEqual(review.bevent, None)

        # Test review with rating None
        review = Review()
        await review.review(ISBN, None, "This is a review", ["tag1", "tag2"])
        self.assertEqual(review.isbn, ISBN)
        self.assertEqual(review.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(review.external_id, "isbn")
        self.assertEqual(review.rating_normal, "NA")
        self.assertEqual(review.rating_raw, "NA")
        self.assertEqual(review.rating, None)
        self.assertEqual(review.content, "NA")
        self.assertEqual(review.tags, [])
        self.assertEqual(review.bevent, None)
    
    async def test_review_build_event_invalid(self):
        """
        Test Review (build_event invalid)
        """
        review = Review()
        self.assertRaises(ValueError, review.build_event)
        review.isbn = ISBN
        self.assertRaises(ValueError, review.build_event)
        review.identifier = hashlib.sha256(ISBN.encode()).hexdigest()
        self.assertRaises(ValueError, review.build_event)
        review.external_id = "isbn"
        self.assertRaises(ValueError, review.build_event)
        review.rating_normal = "1.0"
        self.assertRaises(ValueError, review.build_event)
    
    def test_review_build_event(self):
        """
        Test Review (build_event)
        """
        review = Review()
        review.isbn = ISBN
        review.identifier = hashlib.sha256(ISBN.encode()).hexdigest()
        review.external_id = "isbn"
        review.rating_normal = "1.0"
        review.rating_raw = "5/5"
        review.content = "This is a review"
        review.tags = ["tag1", "tag2"]
        review.build_event()
        event = review.bevent.to_event(KEYS)
        self.assertEqual(event.kind(), Kind(31025))
        self.assertEqual(event.content(), "This is a review")
        tags = event.tags()
        self.assertEqual(tags[0].as_vec()[0], "d")
        self.assertEqual(tags[0].as_vec()[1], hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(tags[1].as_vec()[0], "k")
        self.assertEqual(tags[1].as_vec()[1], "isbn")
        self.assertEqual(tags[2].as_vec()[0], "rating")
        self.assertEqual(tags[2].as_vec()[1], "1.0")
        self.assertEqual(tags[3].as_vec()[0], "raw")
        self.assertEqual(tags[3].as_vec()[1], "5/5")
        self.assertEqual(tags[4].as_vec()[0], "t")
        self.assertEqual(tags[4].as_vec()[1], "#tag1")
        self.assertEqual(tags[5].as_vec()[0], "t")
        self.assertEqual(tags[5].as_vec()[1], "#tag2")

        # Repeat with no content
        review = Review()
        review.isbn = ISBN
        review.identifier = hashlib.sha256(ISBN.encode()).hexdigest()
        review.external_id = "isbn"
        review.rating_normal = "1.0"
        review.rating_raw = "5/5"
        review.content = ""
        review.tags = ["tag1", "tag2"]
        review.build_event()
        event = review.bevent.to_event(KEYS)
        self.assertEqual(event.kind(), Kind(31025))
        self.assertEqual(event.content(), "")
        tags = event.tags()
        self.assertEqual(tags[0].as_vec()[0], "d")
        self.assertEqual(tags[0].as_vec()[1], hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(tags[1].as_vec()[0], "k")
        self.assertEqual(tags[1].as_vec()[1], "isbn")
        self.assertEqual(tags[2].as_vec()[0], "rating")
        self.assertEqual(tags[2].as_vec()[1], "1.0")


    def test_review_parse_event(self):
        """
        Test Review (parse_event)
        """
        kind1 = Kind(31025)
        kind2 = Kind(30250)
        tags = [
            Tag.identifier(hashlib.sha256(ISBN.encode()).hexdigest()),
            Tag.custom(TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.K)),["isbn"]),
            Tag.custom(TagKind.UNKNOWN("rating"), ["1.0"]),
            Tag.custom(TagKind.UNKNOWN("raw"),["5/5"]),
            Tag.hashtag(f"#tag1"),
            Tag.hashtag(f"#tag2")
        ]
        content="This is a review"
        event1 = EventBuilder(kind=kind1, content=content, tags=tags).to_event(keys=KEYS)
        event2 = EventBuilder(kind=kind2, content=content, tags=tags).to_event(keys=KEYS)

        review = Review()
        self.assertRaises(ValueError, review.parse_event, event=event2)
        self.assertRaises(ValueError, review.parse_event, event="This is not an event")

        review = Review().parse_event(event=event1, isbn=ISBN)
        self.assertEqual(review.isbn, ISBN)
        self.assertEqual(review.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(review.external_id, "isbn")
        self.assertEqual(review.rating_normal, "1.0")
        self.assertEqual(review.rating_raw, "5/5")
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.content, "This is a review")
        self.assertEqual(review.tags, ["tag1", "tag2"])
        self.assertEqual(review.bevent, None)

        # Repeat with no content
        event1 = EventBuilder(kind=kind1, content="", tags=tags).to_event(keys=KEYS)
        event2 = EventBuilder(kind=kind2, content="", tags=tags).to_event(keys=KEYS)

        review = Review()
        self.assertRaises(ValueError, review.parse_event, event=event2)
        self.assertRaises(ValueError, review.parse_event, event="This is not an event")

        review = Review().parse_event(event=event1, isbn=ISBN)
        self.assertEqual(review.isbn, ISBN)
        self.assertEqual(review.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(review.external_id, "isbn")
        self.assertEqual(review.rating_normal, "1.0")
        self.assertEqual(review.rating_raw, "5/5")
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.content, "NA")
        self.assertEqual(review.tags, ["tag1", "tag2"])
        self.assertEqual(review.bevent, None)
    
    def test_review_parse_event_misisng_fields(self):
        """
        Test Review (parse_event_missing_fields)
        """
        kind = Kind(31025)
        event = EventBuilder(kind=kind, content="", tags=[]).to_event(keys=KEYS)

        review = Review()
        review.parse_event(event=event, isbn=ISBN)
        self.assertEqual(review.isbn, ISBN)
        self.assertEqual(review.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(review.external_id, "isbn")
        self.assertEqual(review.rating_normal, "NA")
        self.assertEqual(review.rating_raw, "NA")
        self.assertEqual(review.rating, None)
        self.assertEqual(review.bevent, None)
    
    def test_review_parse_event_none(self):
        """
        Test Review (parse_event_none)
        """
        review = Review()
        review.parse_event(event=None, isbn=ISBN)
        self.assertEqual(review.isbn, None)
        self.assertEqual(review.identifier, None)
        self.assertEqual(review.external_id, None)
        self.assertEqual(review.rating_normal, None)
        self.assertEqual(review.rating_raw, None)
        self.assertEqual(review.rating, None)
        self.assertEqual(review.content, None)
        self.assertEqual(review.tags, None)
        self.assertEqual(review.bevent, None)

    async def test_review_detailed(self):
        """
        Test Review (detailed)
        """
        review = await Review().review(ISBN, 5.0, "This is a review", ["tag1", "tag2"])
        self.assertEqual(review.detailed()["id"], hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(review.detailed()["exid"], "isbn")
        self.assertEqual(review.detailed()["rating_normal"], "1.0")
        self.assertEqual(review.detailed()["rating_raw"], "5.0/5")
        self.assertEqual(review.detailed()["rating"], 5.0)
        self.assertEqual(review.detailed()["content"], "This is a review")
        self.assertEqual(review.detailed()["tags"], ["tag1", "tag2"])

        review = await Review().new(ISBN)
        self.assertEqual(review.detailed()["id"], hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(review.detailed()["exid"], "isbn")
        self.assertEqual(review.detailed()["rating_normal"], "NA")
        self.assertEqual(review.detailed()["rating_raw"], "NA")
        self.assertEqual(review.detailed()["rating"], None)
        self.assertEqual(review.detailed()["content"], "NA")
        self.assertEqual(review.detailed()["tags"], [])

    async def test_review_fetch_empty(self):
        """
        Test Review (fetching reviews empty)
        """
        npub = KEYS.public_key().to_bech32()
        relays = {"wss://relay.damus.io": None}
        isbns = [ISBN, ISBN2]
        result = await fetch_reviews(isbns=[], npub=npub, relays=relays)
        self.assertEqual(result, {})
        with self.assertRaises(Exception) as e:
            await fetch_reviews(isbns=None, npub=npub, relays=relays)
        self.assertEqual(str(e.exception), "No ISBNs provided.")
        with self.assertRaises(Exception) as e:
            await fetch_reviews(isbns=["9780141030586"], npub=None, relays=relays)
        self.assertEqual(str(e.exception), "No npub provided or invalid npub.")
        with self.assertRaises(Exception) as e:
            await fetch_reviews(isbns=["9780141030586"], npub="", relays=relays)
        self.assertEqual(str(e.exception), "No npub provided or invalid npub.")
        with self.assertRaises(Exception) as e:
            await fetch_reviews(isbns=["9780141030586"], npub="npub123456", relays=relays)
        self.assertEqual(str(e.exception), "No npub provided or invalid npub.")

        # For empty list create new objects
        result = await fetch_reviews(isbns=isbns, npub=npub, relays=relays)
        new_list = [await Review().new(isbn=isbn) for isbn in isbns]
        detailed_dict = {review.isbn: review.detailed() for review in new_list}
        self.assertEqual(result, detailed_dict)

    @patch('utils.Review.nostr_get')
    async def test_fetch_review(self, mock_nostr_get):
        """
        Test Review (fetching reviews patch)
        """
        # Mock events
        kind = Kind(31025)
        content="A review."

        tags = [
            Tag.identifier(hashlib.sha256(ISBN.encode()).hexdigest()),
            Tag.custom(TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.K)),["isbn"]),
            Tag.custom(TagKind.UNKNOWN("rating"), ["1.0"]),
            Tag.custom(TagKind.UNKNOWN("raw"),["5.0/5"]),
            Tag.hashtag(f"#tag1"),
            Tag.hashtag(f"#tag2")
        ]
        
        event1 = EventBuilder(kind=kind, content=content, tags=tags).to_event(keys=KEYS)
        
        tags = [
            Tag.identifier(hashlib.sha256(ISBN2.encode()).hexdigest()),
            Tag.custom(TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.K)),["isbn"]),
            Tag.custom(TagKind.UNKNOWN("rating"), ["0.5"]),
            Tag.custom(TagKind.UNKNOWN("raw"),["2.5/5"]),
            Tag.hashtag(f"#tag4"),
            Tag.hashtag(f"#tag5")
        ]

        event2 = EventBuilder(kind=kind, content=content, tags=tags).to_event(keys=KEYS)
        events = [event1, event2]

        mock_nostr_get.return_value = events
        actual = await fetch_reviews(isbns=[ISBN, ISBN2, ISBN3], npub=KEYS.public_key().to_bech32(), relays={"wss://relay.damus.io": None})
    
        parsed1 = Review().parse_event(event=event1, isbn=ISBN)
        parsed2 = Review().parse_event(event=event2, isbn=ISBN2)
        new = await Review().new(isbn=ISBN3)

        expected = {ISBN: parsed1.detailed(), ISBN2: parsed2.detailed(), ISBN3: new.detailed()}
        self.assertEqual(actual, expected)

    def tearDown(self):
        pass