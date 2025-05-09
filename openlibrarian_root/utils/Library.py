from nostr_sdk import Tag, Event, EventBuilder, Kind, TagKind, SingleLetterTag, Alphabet, Client, Filter, PublicKey, Event
from utils.Book import Book
from utils.Login import check_npub
from utils.Network import nostr_get
import hashlib, ast, asyncio

section_title_map = {
    "TRS" : "To Read (S)",
    "TRW" : "To Read (W)",
    "CR" : "Currently Reading",
    "HR" : "Have Read",
}

section_description_map = {
    "TRS" : "Books on the shelf ready to read",
    "TRW" : "Books I want to read but do not own yet",
    "CR" : "Books I am currently reading",
    "HR" : "Books I have finished reading",
}

class Library:
    """Library Class. Allows for easy creation and access of library objects."""
    def __init__(self, npub: str = None, read_only: bool = False, **kwargs):
        """Initialize library object"""
        if npub in [None, ""] or check_npub(npub) is False:
            raise Exception("Invalid or missing npub")
        # Default empty library
        if "section" in kwargs.keys():
            if kwargs["section"] not in ["TRS","TRW","CR","HR"]:
                raise Exception("Invalid library section")
            self.section = kwargs["section"]

            # Build identifier
            identifier_str = npub+self.section
            sha1 = hashlib.sha1()
            sha1.update(identifier_str.encode("utf-8"))
            self.identifier = sha1.hexdigest()
            
            self.title = section_title_map[self.section]
            self.description = section_description_map[self.section]
            self.content = "Books & Literature (OpenLibrarian)"
            self.books = []
            self.bevent = None

        # Existing library (dict)
        elif "dict" in kwargs.keys():
            self.section = kwargs["dict"]["s"]
            self.identifier = kwargs["dict"]["i"]
            self.title = kwargs["dict"]["t"]
            self.description = kwargs["dict"]["d"]
            self.content = kwargs["dict"]["c"]
            self.books = kwargs["dict"]["b"]
            self.bevent = None

        # Existing library (Event)
        elif "event" in kwargs.keys():
            if type(kwargs["event"]) != Event:
                raise Exception("Invalid event provided")
            elif kwargs["event"].kind() != Kind(30003):
                raise Exception("Not a library event")
            elif npub in [None, ""] or check_npub(npub) is False:
                raise Exception("No npub provided or value not valid.")
            else:
                event = kwargs["event"]
                # Convert the tags to dictonaries
                tags = event.tags().to_vec()
                tags_dict = {}
                extIDs = []

                for tag in tags:
                    if tag.as_vec()[0] != "i":
                        tags_dict[tag.as_vec()[0]] = tag.as_vec()[1]
                    else:
                        i = tag.as_vec()[1].replace("isbn:","")
                        extIDs.append(Book(isbn=i).concise())
                
                # Handle hidden books
                content_raw = event.content().replace("isbn:","")
                content = content_raw.split(":")
                if int(content[1]) >= 1 and read_only is False:
                    decrypted_tags = ast.literal_eval(content[2])
                    for dtag in decrypted_tags:
                        if dtag[0] == "i":
                            extIDs.append(Book(isbn=dtag[1], hidden="Y").concise())
                elif int(content[1]) >= 1:
                    for i in range(1, int(content[1])+1):
                        extIDs.append(Book(isbn=f"Hidden{i}", hidden="Y").concise())
                if extIDs:
                    tags_dict["i"] = extIDs    
            
                # Check for expected tags
                if "title" not in tags_dict.keys():
                    raise Exception("Missing expected title tag.")
                elif "d" not in tags_dict.keys():
                    raise Exception("Missing expected identifier tag.")
                else:
                    # Check if the identifier is valid
                    section = (list(section_title_map.keys())[list(section_title_map.values()).index(tags_dict["title"])])
                    identifier_str = npub+section
                    sha1 = hashlib.sha1()
                    sha1.update(identifier_str.encode("utf-8"))
                    if sha1.hexdigest() != tags_dict["d"]:
                        raise Exception("Invalid identifier.")
                    else:
                        self.section = section
                        self.identifier = tags_dict["d"]
                        self.title = section_title_map[self.section]
                        self.description = section_description_map[self.section]
                        self.content = "Books & Literature (OpenLibrarian)"
                        if "i" in tags_dict.keys():
                            self.books = tags_dict["i"]
                        else:
                            self.books = []
                        self.bevent = event


    async def get_book_details(self):
        tasks = []
        for book in self.books:
            task = asyncio.create_task(Book(isbn=book["i"], hidden=book["h"]).get_book())
            tasks.append(task)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        self.books = [book.detailed() for book in results if not isinstance(book, Exception)]
        return self

    # Add book to library
    async def add_book(self, **kwargs):
        """Add a book to the library"""
        if "book" in kwargs.keys():
            book = Book(**kwargs)
            self.books.append(book.detailed())
        elif "url" in kwargs.keys():
            if "hidden" in kwargs.keys():
                book = Book(url=kwargs["url"],hidden=kwargs["hidden"])
            else:
                book = Book(url=kwargs["url"])
            await book.get_book()
            self.books.append(book.detailed())
        elif "isbn" in kwargs.keys():
            if "hidden" in kwargs.keys():
                book = Book(isbn=kwargs["isbn"],hidden=kwargs["hidden"])
            else:
                book = Book(isbn=kwargs["isbn"])
            await book.get_book()
            self.books.append(book.detailed())
        elif "dict" in kwargs.keys():
            self.books.append(kwargs["dict"])
        else:
            raise Exception("Invalid book or url provided")
        return self

    # Remove book from library
    async def remove_book(self, **kwargs):
        """Remove a book from the library"""
        if "book" in kwargs.keys():
            self.books.remove(kwargs["book"])
        elif "url" in kwargs.keys():
            book = Book(url=kwargs["url"])
            await book.get_book()
            self.books.remove(book.detailed())
        elif "isbn" in kwargs.keys():
            for book in self.books:
                if book["i"] == kwargs["isbn"]:
                    ind = self.books.index(book)
                    del self.books[ind]
        else:
            raise Exception("Invalid book or url provided")

    # Build event
    def build_event(self, npub: str = None):
        """Build event from library object"""
        if npub in [None, ""] or check_npub(npub) is False:
            raise Exception("No npub provided or invalid npub.")
        
        # Events Kind and Main tags
        kind = Kind(30003)
        tags = [
            Tag.identifier(self.identifier),
            Tag.custom(TagKind.TITLE(),[self.title]),
            Tag.custom(TagKind.DESCRIPTION(),[self.description]),
        ]

        # Append book tags
        hidden_items = []
        for book in self.books:
            book_obj = Book(dict=book).concise()
            clean_isbn = book_obj["i"].replace("-","")
            tag = Tag.custom(TagKind.SINGLE_LETTER(single_letter=SingleLetterTag.lowercase(Alphabet.I)),[f'isbn:{clean_isbn}'])
            if book_obj["h"] == "Y":
                hidden_items.append(tag.as_vec())
            else:
                tags.append(tag)

        # Build content (include hidden items)
        if hidden_items:
            content = f"{self.content}:{len(hidden_items)}:{hidden_items}"
        else:
            content = f"{self.content}:0"
        
        # Build event
        builder = EventBuilder(
            kind = kind,
            content = content
        ).tags(tags)

        self.bevent = builder

        return self

    def __dict__(self):
        """Return library object as dictionary"""
        return {
            "s":self.section,
            "i":self.identifier,
            "t":self.title,
            "d":self.description,
            "c":self.content,
            "b":self.books
        }

async def fetch_libraries(npub: str = None, relays: dict = None):
    """Fetch libraries from relays"""
    # Check if npub is valid
    if npub in [None, ""] or check_npub(npub) is False:
        raise Exception("No npub provided or invalid npub.")
    else:
        # Get identifiers for events
        ids = []
        library_id = {}
        for section in section_title_map.keys():
            identifier_str = npub+section
            sha1 = hashlib.sha1()
            sha1.update(identifier_str.encode("utf-8"))
            id = sha1.hexdigest()
            ids.append(id)
            library_id[id] = section

        # Filter and fetch events
        filter = Filter().author(PublicKey.parse(npub)).kinds([Kind(30003)]).identifiers(ids).limit(50)
        fetched = await nostr_get(wait=10, filters={"libraries":filter}, relays_dict=relays)
        events = fetched.get("libraries", None)

        # Sort to the latest of each event by ID
        if events:
            events = sorted(events, key=lambda event: event.created_at().as_secs(), reverse=True)

        # Keep just first of each event by ID
        raw_libraries = []
        for event in events:
            if event.tags().identifier() not in raw_libraries:
                raw_libraries.append(event.as_json())
    
        return raw_libraries
    

# Function to prepare fetched Library objects from relays
async def prepare_libraries(libEvents: list=None, npub: str=None, read_only: bool=False):
    """Build libraries from events"""
    # Check list of events have been provided
    if libEvents == None:
        raise Exception("No events provided.")
    elif npub in [None, ""] or check_npub(npub) is False:
        raise Exception("No npub provided or invalid npub.")
    else:
        # Get identifiers for events
        ids = []
        library_id = {}
        for section in section_title_map.keys():
            identifier_str = npub+section
            sha1 = hashlib.sha1()
            sha1.update(identifier_str.encode("utf-8"))
            id = sha1.hexdigest()
            ids.append(id)
            library_id[id] = section

        events = []
        if len(libEvents) > 0:
            for each in libEvents:
                evt = Event.from_json(each)
                dtag = evt.tags().identifier()
                if dtag in ids:
                    events.append(evt)

        # Build list of parsed libraries
        libraries = []
        async def parse_libraries(event):
            library = Library(event=event, npub=npub, read_only=read_only)
            await library.get_book_details()
            ids.remove(library.identifier)
            return library.__dict__()
        tasks = []

        for e in events:
            task = asyncio.create_task(parse_libraries(e))
            tasks.append(task)
        libraries = await asyncio.gather(*tasks)
        
        # Add in missing libraries
        if len(ids) > 0:
            for id in ids:
                library = Library(section=library_id[id],npub=npub)
                libraries.append(library.__dict__())

        return libraries
