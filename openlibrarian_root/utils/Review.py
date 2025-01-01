from nostr_sdk import Event, EventBuilder, Kind, Tag, TagKind, Keys, SingleLetterTag, Alphabet, Filter, PublicKey, Client, NostrSigner
from utils.Login import check_npub, check_nsec
from utils.Network import nostr_get, nostr_post
import aiohttp, datetime, hashlib, os, asyncio, tenacity

class Review:
    def __init__(self):
        self.isbn = None
        self.identifier = None
        self.external_id = None
        self.rating_normal = None
        self.rating_raw = None
        self.rating = None
        self.content = None
        self.tags = None
        self.bevent = None

    def new(self, isbn: str = None):
        """
        Set new review object
        input: isbn (str)
        output: self (Review object)
        """    
        self.isbn = isbn
        self.identifier = hashlib.sha256(isbn.encode()).hexdigest()
        self.external_id = "isbn"
        self.rating_normal = "NA"
        self.rating_raw = "NA"
        self.rating = None
        self.content = "NA"
        self.tags = []
        self.bevent = None
    
    def review(self, isbn: str = None, rating: int = None, content: str = None, tags: list = None, max=5):
        if self.isbn is None:
            self.new(isbn)
        
        # Check for valid rating
        if rating is None or type(rating) != int:
            return self
        else:
            self.rating = rating
            self.rating_raw = f"{rating}/{max}"
            self.rating_normal = f"{rating / max}"

            if content is not None:
                self.content = content
            if tags is not None:
                self.tags = tags

        return self

    def parse_event(self, event: Event = None, isbn: str = None):
        """
        Parse event into review object
        input: event (Event)
        output: self (Review object)
        """
        if event is None:
            return self
        elif type(event) != Event:
            raise ValueError("Invalid event type")
        elif event.kind() != Kind(31025):
            raise ValueError("Invalid event kind")
        else:
            self.isbn = isbn
            tags = event.tags()
            for tag in tags:
                if tag.as_vec()[0] == "d":
                    self.identifier = tag.as_vec()[1]
                elif tag.as_vec()[0] == "k":
                    self.external_id = tag.as_vec()[1]
                elif tag.as_vec()[0] == "rating":
                    self.rating_normal = tag.as_vec()[1]
                    self.rating = float(self.rating_normal)*5
                elif tag.as_vec()[0] == "raw":
                    self.rating_raw = tag.as_vec()[1]
                
            self.tags = []
            for tag in tags:
                if tag.as_vec()[0] == "t":
                    self.tags.append(tag.as_vec()[1].replace("#", ""))
            
            if event.content() != "":
                self.content = event.content()
            else:
                self.content = "NA"

            # Populate missing fields
            if self.identifier is None:
                self.identifier = hashlib.sha256(self.isbn.encode()).hexdigest()
            if self.external_id is None:
                self.external_id = "isbn"
            if self.rating_normal is None:
                self.rating_normal = "NA"
            if self.rating_raw is None:
                self.rating_raw = "NA"
            if self.content is None:
                self.content = "NA"
            if self.tags is None:
                self.tags = []

            # Set bevent
            self.bevent = None
        
        return self
    
    def build_event(self):
        """
        Build event from library object
        output: self (Progress object)
        """
        if self.isbn is None:
            raise ValueError("ISBN not set")
        if self.identifier is None:
            raise ValueError("Identifier not set")
        if self.external_id is None:
            raise ValueError("External ID not set")
        if self.rating_normal is None:
            raise ValueError("Rating not set")
        if self.rating_raw is None:
            raise ValueError("Rating Raw not set")
        
        # Events Kind and Main tags
        kind = Kind(31025)
        tags = [
            Tag.identifier(self.identifier),
            Tag.custom(TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.K)),["isbn"]),
            Tag.custom(TagKind.UNKNOWN("rating"), [self.rating_normal]),
            Tag.custom(TagKind.UNKNOWN("raw"),[self.rating_raw]),
        ]
        if self.tags not in ([], None):
            for tag in self.tags:
                tags.append(Tag.hashtag(f"#{tag}"))
        if self.content is not None:
            content = f"{self.content.strip()}"
        else:
            content = ""

        # Build event
        builder = EventBuilder(
            kind = kind,
            tags = tags,
            content = content
        )
        self.bevent = builder

        return self
    
    