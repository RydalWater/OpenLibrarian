from django.test import TestCase
from nostr_sdk import EventBuilder, Keys, Kind, Tag, TagKind, SingleLetterTag, Alphabet
import datetime, hashlib, sys, io
from aioresponses import aioresponses
from unittest.mock import patch
from utils.Review import Review

KEYS = Keys.generate()
ISBN = "9780141030586"

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

    def test_review_new(self):
        """
        Test Review (new)
        """
        review = Review()
        review.new(ISBN)
        self.assertEqual(review.isbn, ISBN)
        self.assertEqual(review.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(review.external_id, "isbn")
        self.assertEqual(review.rating_normal, "NA")
        self.assertEqual(review.rating_raw, "NA")
        self.assertEqual(review.rating, None)
        self.assertEqual(review.content, "NA")
        self.assertEqual(review.tags, [])
        self.assertEqual(review.bevent, None)

    def test_review_review(self):
        """
        Test Review (review)
        """
        review = Review()
        review.review(ISBN, 5, "This is a review", ["tag1", "tag2"])
        self.assertEqual(review.isbn, ISBN)
        self.assertEqual(review.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(review.external_id, "isbn")
        self.assertEqual(review.rating_normal, "1.0")
        self.assertEqual(review.rating_raw, "5/5")
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.content, "This is a review")
        self.assertEqual(review.tags, ["tag1", "tag2"])
        self.assertEqual(review.bevent, None)
    
    def test_review_build_event(self):
        """
        Test Review (build_event)
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
        print(review)
        self.assertEqual(review.isbn, ISBN)
        self.assertEqual(review.identifier, hashlib.sha256(ISBN.encode()).hexdigest())
        self.assertEqual(review.external_id, "isbn")
        self.assertEqual(review.rating_normal, "1.0")
        self.assertEqual(review.rating_raw, "5/5")
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.content, "This is a review")
        self.assertEqual(review.tags, ["tag1", "tag2"])
        self.assertEqual(review.bevent, None)

    def tearDown(self):
        pass