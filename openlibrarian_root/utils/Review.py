from nostr_sdk import Event, EventBuilder, Kind, Tag, TagKind, SingleLetterTag, Alphabet, Filter, PublicKey, Client
from utils.Login import check_npub
from utils.Network import nostr_get
from utils.General import remove_dups_on_id
import hashlib, asyncio

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

    async def new(self, isbn: str = None):
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
        self.content = ""
        self.tags = []
        self.bevent = None

        return self
    
    async def review(self, isbn: str = None, rating: float = None, content: str = None, tags: list = None, max=5):
        if self.isbn is None:
            await self.new(isbn)
        
        # Check for valid rating
        if rating is None or type(rating) != float:
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
            tags = event.tags().to_vec()
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
                self.content = ""

            # Populate missing fields
            if self.identifier is None:
                self.identifier = hashlib.sha256(self.isbn.encode()).hexdigest()
            if self.external_id is None:
                self.external_id = "isbn"
            if self.rating_normal is None:
                self.rating_normal = "NA"
            if self.rating_raw is None:
                self.rating_raw = "NA"

            # Set bevent
            self.bevent = None
        
        return self
    
    def build_event(self):
        """
        Build event from library object
        output: self (review object)
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
                tags.append(Tag.hashtag(f"{tag}"))
        if self.content not in(None, ""):
            content = f"{self.content.strip()}"
        else:
            content = ""

        # Build event
        builder = EventBuilder(
            kind = kind,
            content = content
        ).tags(tags)
        
        self.bevent = builder

        return self
    
    def __dict__(self):
        """
        Return review object as dictionary
        output: dict
        """
        return {
            "id": self.identifier,
            "exid": self.external_id,
            "rating": self.rating,
            "content": self.content,
            "tags": self.tags,
            "rating_normal": self.rating_normal,
            "rating_raw": self.rating_raw,
        }

    def detailed(self):
        """
        Return detailed review object as dictionary
        output: dict
        """
        return self.__dict__()


# Fetch review objects
async def fetch_reviews(npub: str, relays: dict, isbns: list = None):
    """
    Fetch reviews objects from relays
    input: npub (str), relays (dict), isbns (list)
    output: dict
    """
    # Check inputs are valid
    if isbns == []:
        return {}
    elif isbns == None:
        raise Exception("No ISBNs provided.")
    elif npub in [None, ""] or check_npub(npub) is False:
        raise Exception("No npub provided or invalid npub.")
    else:
        id_isbn_map = {hashlib.sha256(isbn.encode()).hexdigest(): isbn for isbn in isbns}
        ids = id_isbn_map.keys()

        # Filter and fetch events
        filter = Filter().author(PublicKey.parse(npub)).kinds([Kind(31025)]).identifiers(ids).limit(2100)
        fetched = await nostr_get(wait=10, filters={"reviews":filter}, relays_dict=relays)
        events = fetched.get("reviews", None)
        
        if events in [None, []]:
            # Create new review objects
            for isbn in isbns:
                new_tasks = [Review().new(isbn=isbn) for isbn in isbns]
                review_events = await asyncio.gather(*new_tasks)

            return {review_event.isbn: review_event.detailed() for review_event in review_events}

        # Remove duplicates by identifier       
        unique_events = remove_dups_on_id(events, "review")

        # Parse events
        review_events = []
        for event in unique_events:
            if event.tags().identifier() in ids:
                isbn = id_isbn_map[event.tags().identifier()]
                review_events.append(Review().parse_event(event,isbn=isbn))

        # Get new review objects for all isbns where events are not availabe
        new_isbns = []
        for isbn in isbns:
            if isbn not in [review_event.isbn for review_event in review_events]:
                new_isbns.append(isbn)

        # Set up new review objects as tasks
        new_tasks = [Review().new(isbn=new) for new in new_isbns]
        
        # Async gather all tasks
        review_all = await asyncio.gather(*new_tasks)
        review_all.extend(review_events)
        
        # Convert to dictionaries and return
        return {review.isbn: review.detailed() for review in review_all}
