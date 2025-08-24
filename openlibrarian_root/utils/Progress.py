from nostr_sdk import (
    Event,
    EventBuilder,
    Kind,
    Tag,
    TagKind,
    SingleLetterTag,
    Alphabet,
    Filter,
    PublicKey,
)
from utils.Login import check_npub
from utils.Network import nostr_get
from utils.General import remove_dups_on_id
import aiohttp
import datetime
import hashlib
import os
import asyncio
import tenacity

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

    async def new(self, isbn: str = None, default_pages: int = None):
        """
        Set new progress object with isbn
        input: isbn (str)
        output: self (Progress object)
        """
        self.isbn = isbn
        self.identifier = hashlib.sha256(isbn.encode()).hexdigest()
        self.external_id = "isbn"
        self.unit = "pages"
        self.current = "0"
        self.started = "NA"
        self.ended = "NA"
        self.bevent = None
        if default_pages is not None and int(default_pages) > 0:
            self.default_pages = str(default_pages)
        else:
            await self.get_default_pages()
        self.max = str(self.default_pages)
        self.progress = "0"
        return self

    def start_book(self, started: str = None):
        """
        Set started date
        input: started (str) format: "YYYY-MM-DD", optional
        output: self (Progress object)
        """
        if self.ended not in (None, "NA"):
            self.ended = "NA"
        if self.current not in (None, "0"):
            self.current = "0"
            self.progress = "0"
        if started is not None:
            self.started = started
        else:
            self.started = datetime.datetime.now().strftime("%Y-%m-%d")
        return self

    def end_book(self, ended: str = None):
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

    def update_progress(self, current: str = None, max: str = None, unit: str = None):
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
            if (changed or self.max in (None, "0")) and max is None:
                self.max = self.default_pages

        # Calculate progress
        if self.unit == "pct":
            self.progress = self.current
        elif self.unit == "pages":
            if int(self.max) < int(self.current):
                raise ValueError("Current pages cannot be greater than max pages")
            self.progress = str(round((int(self.current) / int(self.max)) * 100))

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
        elif type(event) is not Event:
            raise ValueError("Invalid event type")
        elif event.kind() != Kind(30250):
            raise ValueError("Invalid event kind")
        else:
            self.isbn = isbn
            tags = event.tags().to_vec()
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

            # Populate missing fields
            if self.identifier is None:
                self.identifier = hashlib.sha256(self.isbn.encode()).hexdigest()
            if self.external_id is None:
                self.external_id = "isbn"
            if self.unit is None:
                self.unit = "pages"
            if self.current is None:
                self.current = "0"
            if self.max is None:
                self.max = "0"
            if self.started is None:
                self.started = "NA"
            if self.ended is None:
                self.ended = "NA"

            # Set bevent and default_pages
            self.bevent = None
            self.default_pages = None

            # Prevent negative values
            try:
                int_current = int(self.current)
            except ValueError as e:
                print(f"Error converting current to int: {e}")
                int_current = False
            try:
                int_max = int(self.max)
            except ValueError as e:
                print(f"Error converting max to int: {e}")
                int_max = False

            if int_current < 0 or not int_current:
                self.current = "0"
            if int_max < 0 or not int_max:
                self.max = "0"

            # Handle progress (pct)
            if self.unit == "pct":
                self.max = "100"
                if int_current > 100:
                    self.current = "100"
                    self.progress = "100"
                else:
                    self.progress = self.current
            # Handle progress (pages)
            elif self.unit == "pages":
                if int_current > int_max:
                    self.max = self.current
                    self.progress = "100"
                elif int_max == 0:
                    self.progress = "0"
                elif int_current == 0:
                    self.progress = "0"
                else:
                    self.progress = str(round((int_current / int_max) * 100))
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
        elif type(data) is not dict:
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
    @tenacity.retry(
        wait=tenacity.wait_fixed(3), stop=tenacity.stop_after_attempt(3), reraise=True
    )
    async def get_default_pages(self):
        """
        Get default pages for progress
        output: self (Progress object)
        """
        if self.isbn is None:
            raise ValueError("ISBN not set")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"https://openlibrary.org/isbn/{self.isbn}.json",
                    headers=headers,
                    timeout=8,
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "number_of_pages" in data:
                            self.default_pages = str(data["number_of_pages"])
                            return self

            except Exception:
                pass

            try:
                async with session.get(
                    f"{alt_api_url}", params={"q": "isbn:" + self.isbn}, timeout=8
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if (
                            "items" in data
                            and "pageCount" in data["items"][0]["volumeInfo"]
                        ):
                            self.default_pages = str(
                                data["items"][0]["volumeInfo"]["pageCount"]
                            )
                            return self

            except Exception:
                pass

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
            Tag.custom(
                TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.K)), ["isbn"]
            ),
            Tag.custom(TagKind.UNKNOWN("unit"), [self.unit]),
            Tag.custom(TagKind.UNKNOWN("current"), [self.current]),
            Tag.custom(TagKind.UNKNOWN("max"), [self.max]),
            Tag.custom(TagKind.UNKNOWN("started"), [self.started]),
            Tag.custom(TagKind.UNKNOWN("ended"), [self.ended]),
        ]
        content = ""

        # Build event
        builder = EventBuilder(kind=kind, content=content).tags(tags)

        self.bevent = builder

        return self

    def __dict__(self):
        """
        Return progress object as dictionary
        output: dict
        """
        return {
            "id": self.identifier,
            "exid": self.external_id,
            "unit": self.unit,
            "curr": self.current,
            "max": self.max,
            "st": self.started,
            "en": self.ended,
            "default": self.default_pages,
            "progress": self.progress,
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
    input: npub (str), relays (dict), isbns (list)
    output: dict
    """
    # Check inputs are valid
    if isbns == []:
        return {}
    elif isbns is None:
        raise Exception("No ISBNs provided.")
    elif npub in [None, ""] or check_npub(npub) is False:
        raise Exception("No npub provided or invalid npub.")
    else:
        id_isbn_map = {
            hashlib.sha256(isbn.encode()).hexdigest(): isbn for isbn in isbns
        }
        ids = id_isbn_map.keys()

        # Filter and fetch events
        filter = (
            Filter()
            .author(PublicKey.parse(npub))
            .kinds([Kind(30250)])
            .identifiers(ids)
            .limit(2100)
        )
        fetched = await nostr_get(
            wait=10, filters={"progress": filter}, relays_dict=relays
        )
        events = fetched.get("progress", None)

        if events in [None, []]:
            # Create new progress objects
            for isbn in isbns:
                new_tasks = [Progress().new(isbn=isbn) for isbn in isbns]
                progress_events = await asyncio.gather(*new_tasks)

            return {
                progress_event.isbn: progress_event.detailed()
                for progress_event in progress_events
            }

        # Remove duplicates by identifier
        unique_events = remove_dups_on_id(events, "progress")

        # Parse events
        progress_events = []
        for event in unique_events:
            if event.tags().identifier() in ids:
                isbn = id_isbn_map[event.tags().identifier()]
                progress_events.append(Progress().parse_event(event, isbn=isbn))

        # Set up get_default_pages as tasks
        tasks = [
            progress_event.get_default_pages() for progress_event in progress_events
        ]

        # Get new progress objects for all isbns where events are not availabe
        new_isbns = []
        for isbn in isbns:
            if isbn not in [progress_event.isbn for progress_event in progress_events]:
                new_isbns.append(isbn)

        # Set up new progress objects as tasks
        new_tasks = [Progress().new(isbn=new) for new in new_isbns]

        # Async gather all tasks
        progress_all = await asyncio.gather(*(tasks + new_tasks))

        # Convert to dictionaries and return
        return {progress.isbn: progress.detailed() for progress in progress_all}
