from nostr_sdk import Event, EventBuilder, Kind, Tag, TagKind, Keys, SingleLetterTag, Alphabet, Filter, PublicKey, Client, NostrSigner
from utils.Login import check_npub, check_nsec, check_npub_of_nsec
from utils.Network import nostr_get, nostr_post
import aiohttp, datetime, hashlib, os, asyncio

email_address = os.getenv("EMAIL_ADDY")

headers = {
    "User-Agent": f"Open Librarian (A FOSS book tracker powered by Nostr) - {email_address}",
}

alt_api_url = "https://www.googleapis.com/books/v1/volumes"

class Progress:
    def __init__(self):
        self.identifier = None
        self.isbn = None
        self.external_id = None
        self.unit = None
        self.current = None
        self.max = None
        self.started = None
        self.ended = None
        self.bevent = None
        self.default_pages = None
        self.progress = None
    
    async def new(self, isbn: str=None):
        """
        Set new progress object with isbn
        input: isbn (str)
        """
        self.isbn = isbn
        self.identifier = hashlib.sha256(isbn.encode()).hexdigest()
        self.external_id = "isbn"
        self.unit = "pages"
        self.current = "0"
        self.started = "NA"
        self.ended = "NA"
        self.bevent = None
        await self.get_default_pages()
        self.max = str(self.default_pages)
        self.progress = "0"
        return self

    def start_book(self, started: str=None):
        """
        Set started date
        input: started (str) format: "YYYY-MM-DD", optional
        output: self (Progress object)
        """
        if self.ended not in (None, "NA"):
            raise ValueError("Book already ended")
        if started is not None:
            self.started = started
        else:
            self.started = datetime.datetime.now().strftime("%Y-%m-%d")
        return self

    def end_book(self, ended: str=None):
        """
        Set ended date
        input: ended (str) format: "YYYY-MM-DD", optional
        output: self (Progress object)
        """
        if self.started in (None, "NA"):
            raise ValueError("Book not started")
        if ended is not None:
            self.ended = ended
        else:
            self.ended = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Set current to max if not set
        if self.unit == "pct":
            self.current = "100"
            self.max = "100"
        elif self.unit == "pages":
            if self.max not in (None, "0"):
                self.current = self.max
            elif self.default_pages not in (None, "NOT AVAILABLE"):
                self.current = self.default_pages
                self.max = self.default_pages
        
        self.progress = "100"

        return self

    def update_progress(self, current: str=None, max: str=None, unit: str=None):
        """
        Update progress
        input: current (str), max (str)
        output: self (Progress object)
        """
        if self.started in (None, "NA"):
            self.start_book()
        if current is None:
            raise ValueError("Current not set")
        if unit is not None and unit not in ("pct", "pages"):
            raise ValueError("Invalid unit")
        if unit is not None and unit != self.unit:
            self.unit = unit
            changed = True
        else:
            changed = False

        self.current = current
        if max is not None:
            self.max = max
        elif self.unit == "pct":
            self.max = "100"
        elif self.unit == "pages":
            if (changed or self.max in (None, "0")) and max == None:
                self.max = self.default_pages

        # Calculate progress
        if self.unit == "pct":
            self.progress = self.current
        elif self.unit == "pages":
            if int(self.max) < int(self.current):
                raise ValueError("Current pages cannot be greater than max pages")
            self.progress = str(round((int(self.current)/int(self.max))*100))

        # Reset ended if progress is not 100
        if self.progress != "100":
            self.ended = "NA"

        return self
    
    def parse_event(self, event: Event = None, isbn: str = None):
        """
        Parse event and update progress object
        input: event (Event), isbn (str)
        output: self (Progress object)
        """
        if event is None:
            return self
        elif type(event) != Event:
            raise ValueError("Invalid event type")
        elif event.kind() != Kind(30250):
            raise ValueError("Invalid event kind")
        else:
            self.isbn = isbn
            tags = event.tags()
            for tag in tags:
                if tag.as_vec()[0] == "d":
                    self.identifier = tag.as_vec()[1]
                elif tag.as_vec()[0] == "k":
                    self.external_id = tag.as_vec()[1]
                elif tag.as_vec()[0] == "unit":
                    self.unit = tag.as_vec()[1]
                elif tag.as_vec()[0] == "current":
                    self.current = tag.as_vec()[1]
                elif tag.as_vec()[0] == "max":
                    self.max = tag.as_vec()[1]
                elif tag.as_vec()[0] == "started":
                    self.started = tag.as_vec()[1]
                elif tag.as_vec()[0] == "ended":
                    self.ended = tag.as_vec()[1]
            self.bevent = None
            self.default_pages = None
            if self.unit == "pct":
                self.progress = self.current
            elif self.unit == "pages":
                if int(self.max) < int(self.current):
                    raise ValueError("Current pages cannot be greater than max pages")
                self.progress = str(round((int(self.current)/int(self.max))*100))
            return self
    
    # Parse from dictionary
    def parse_dict(self, data: dict = None):
        """
        Parse dictionary and update progress object
        input: data (dict)
        output: self (Progress object)
        """
        if data in (None, {}):
            return self
        elif type(data) != dict:
            raise ValueError("Invalid data type")
        else:
            for isbn, values in data.items():
                self.isbn = isbn
                self.identifier = values["id"]
                self.external_id = values["exid"]
                self.unit = values["unit"]
                self.current = values["curr"]
                self.max = values["max"]
                self.started = values["st"]
                self.ended = values["en"]
                self.bevent = None
                self.default_pages = values["default"]
                self.progress = values["progress"]
            return self
    
    # Get default pages for progress
    async def get_default_pages(self):
        """
        Get default pages for progress
        output: self (Progress object)
        """
        if self.isbn is None:
            raise ValueError("ISBN not set")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://openlibrary.org/isbn/{self.isbn}.json", headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if "number_of_pages" in data:
                        self.default_pages = str(data["number_of_pages"])
                        return self
                
                async with session.get(f"{alt_api_url}",params={"q": "isbn:" + self.isbn}, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.default_pages = str(data["items"][0]["volumeInfo"]["pageCount"])
                        return self           
        self.default_pages = "NOT AVAILABLE"
        return self
    
    # Build event
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
        if self.unit is None:
            raise ValueError("Unit not set")
        if self.current is None:
            raise ValueError("Current not set")
        if self.max is None:
            raise ValueError("Max not set")
        if self.started is None:
            raise ValueError("Started not set")
        if self.ended is None:
            raise ValueError("Ended not set")
                
        # Events Kind and Main tags
        kind = Kind(30250)
        tags = [
            Tag.identifier(self.identifier),
            Tag.custom(TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.K)),["isbn"]),
            Tag.custom(TagKind.UNKNOWN("unit"), [self.unit]),
            Tag.custom(TagKind.UNKNOWN("current"),[self.current]),
            Tag.custom(TagKind.UNKNOWN("max"), [self.max]),
            Tag.custom(TagKind.UNKNOWN("started"), [self.started]),
            Tag.custom(TagKind.UNKNOWN("ended"), [self.ended]),
        ]
        content = ""

        # Build event
        builder = EventBuilder(
            kind = kind,
            tags = tags,
            content = content
        )
        self.bevent = builder

        return self

    async def publish_event(self, nym_relays: dict = None, nsec: str = None):
        """
        Publish event from library object
        input: nym_relays (dict), nsec (str)
        output: str
        """

        # Return error if missing required information and is valid
        if nsec in [None, ""] or check_nsec(nsec) is False:
            raise Exception("No nsec provided or invalid nsec.")
        elif self.bevent is None or nym_relays is None or nsec is None:
            raise Exception("Missing required information.")
        elif type(self.bevent) != EventBuilder:
            raise Exception("Not a valid builder object.")
        else:
            # Instantiate client and set signer
            signer = NostrSigner.keys(Keys.parse(nsec))
            client = Client(signer)

            # Post event
            try:
                await nostr_post(client=client, eventbuilder=self.bevent, relays_dict=nym_relays)
                return "Published event."

            except Exception as e:
                return f"Unable to published event: {e}"
    
    def __dict__(self):
        """
        Return progress object as dictionary
        output: dict
        """
        return {
            self.isbn: {
                "id": self.identifier,
                "exid": self.external_id,
                "unit": self.unit,
                "curr": self.current,
                "max": self.max,
                "st": self.started,
                "en": self.ended,
                "default": self.default_pages,
                "progress": self.progress
            }
        }

    def detailed(self):
        """
        Return detailed progress object as dictionary
        output: dict
        """
        return self.__dict__()

# Fetch progress objects
async def fetch_progress(npub: str, relays: dict, isbns: list = None):
    """
    Fetch progress objects from relays
    input: npub (str), relays (dict), nsec (str), isbns (list)
    output: list
    """
    # Check if npub and nsec are valid
    if isbns == []:
        return []
    elif isbns == None:
        raise Exception("No ISBNs provided.")
    elif npub in [None, ""] or check_npub(npub) is False:
        raise Exception("No npub provided or invalid npub.")
    else:
        ids = [hashlib.sha256(isbn.encode()).hexdigest() for isbn in isbns]

        # Instantiate client and set signer
        filter = Filter().author(PublicKey.from_bech32(npub)).kinds([Kind(30250)]).identifiers(ids).limit(2100)
        client = Client(None)

        # get events
        events = await nostr_get(client=client, wait=10, filters=[filter], relays_dict=relays)
        if events in [None, []]:
            # Create new progress objects
            for isbn in isbns:
                new_tasks = [Progress().new(isbn=isbn) for isbn in isbns]
                progress_events = await asyncio.gather(*new_tasks)

            return [progress_events.detailed() for progress_events in progress_events]

        # Parse events
        progress_events = []
        for event in events:
            progress_events.append(Progress().parse_event(event))
        
        # Run get_default_pages as tasks and gather
        tasks = [progress_event.get_default_pages() for progress_event in progress_events]
        progress_events = await asyncio.gather(*tasks)

        # Convert to dictionaries and return
        for isbn in isbns:
            if isbn not in [progress_event.isbn for progress_event in progress_events]:
                new_tasks = [Progress().new(isbn=isbn) for isbn in isbns]
                additional_progress = await asyncio.gather(*new_tasks)
                progress_events = progress_events + additional_progress
        return [progress_events.detailed() for progress_events in progress_events]
