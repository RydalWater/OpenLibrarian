import aiohttp, asyncio, os

alt_api_url = "https://www.googleapis.com/books/v1/volumes"

email_address = os.getenv("EMAIL_ADDY")

headers = {
    "User-Agent": f"Open Librarian (A FOSS book tracker powered by Nostr) - {email_address}",
}

async def get_cover(session: aiohttp.ClientSession, isbn: str, size: str):
    """Get cover image from Open Library API"""
    image = f"https://covers.openlibrary.org/b/isbn/{isbn}-{size}.jpg"
    try:
        async with session.get(image) as response:
            if response.status == 200 and "content-type" in response.headers:
                return image
    except Exception as e:
        pass

    try:
        response = await session.get(alt_api_url, params={"q": "isbn:" + isbn}, timeout=10)
        if response.status == 200:
            data = await response.json()
            if "items" in data and "imageLinks" in data["items"][0]["volumeInfo"]:
                image = data["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
                try:
                    async with session.get(image) as response:
                        if "content-type" in response.headers:
                            return image
                except Exception as e:
                    pass
    except Exception as e:
        pass

    return "N"

class Book:
    """
    Book Class. Allows for easy creation and access of book objects.
    """
    def __init__(self, **kwargs):
        """Initialize book object"""
        if "dict" in kwargs.keys():
            self.isbn = kwargs["dict"]["i"]
            self.url = f"https://openlibrary.org/isbn/{self.isbn}.json"
            self.title = kwargs["dict"]["t"]
            self.author = kwargs["dict"]["a"]
            self.cover = kwargs["dict"]["c"]
            self.hidden = kwargs["dict"]["h"]
        else:
            if "isbn" in kwargs.keys():
                self.isbn = "".join(kwargs["isbn"].split("-"))
                if "Hidden" in self.isbn:
                    self.url = ""
                else:
                    self.url = f"https://openlibrary.org/isbn/{self.isbn}.json"
            elif "url" in kwargs.keys():
                self.isbn = kwargs["url"].split("/")[4].split(".")[0]
                self.url = kwargs["url"] 
            if "Hidden" in self.isbn:   
                self.title = "Mysterious Book"
                self.author = "Unknown Author"
                self.cover = "M"
            else:   
                self.title = None
                self.author = None
                self.cover = None
            if "hidden" in kwargs.keys():
                self.hidden = kwargs["hidden"]
            else:
                self.hidden = "N"
    
    async def get_book(self):
        """Get book information from Open Library API using ISBN endpoint (falling back to google books API)"""
        if self.url != "":
            alt_api = False
            alt_url = ""
            async with aiohttp.ClientSession() as session:
                if self.author is None:
                    # Trying the first connection
                    try:
                        async with session.get(self.url, headers=headers) as response:
                            if response.status == 200:
                                response_json = await response.json()
                                self.title = response_json["title"]
                                if self.title is None:
                                    raise Exception("Cannot find title, trying google books API")

                                if "authors" in response_json:
                                    author_urls = [f"https://openlibrary.org{author['key']}.json" for author in response_json["authors"] if author.get('key')]
                                    author_responses = await asyncio.gather(*[self.fetch_author(session, url) for url in author_urls])
            
                                    authors = [author["name"] for author in author_responses if author]
                                    self.author = ", ".join(authors)
                                if self.author is None:
                                    self.author = "Unknown Author"
                            else:
                                alt_api = True
                                alt_url = f"{alt_api_url}?q=isbn:{self.isbn}"
                    except Exception as e:
                        alt_api = True
                        alt_url = f"{alt_api_url}?q=isbn:{self.isbn}"
                    
                    # Trying the second connection if the first failed (without exception)
                    try:
                        if alt_api:
                            async with session.get(alt_url, headers=headers) as response:
                                if response.status == 200:
                                    response_json = await response.json()
                                    # Check for title in response
                                    if "items" in response_json and "volumeInfo" in response_json["items"][0] and "title" in response_json["items"][0]["volumeInfo"]:
                                        self.title = response_json["items"][0]["volumeInfo"]["title"]

                                    # Check for authors in response
                                    if "items" in response_json and "volumeInfo" in response_json["items"][0] and "authors" in response_json["items"][0]["volumeInfo"]:
                                        authors = [author for author in response_json["items"][0]["volumeInfo"]["authors"]]
                                        self.author = ", ".join(authors)
                                    
                                    if self.title is None:
                                        self.title = "Cannot find title"
                                    if self.author is None:
                                        self.author = "Cannot find author"
                                        
                                else:
                                    self.title = "Cannot find title (API Down)"
                                    self.author = "Cannot find author (API Down)"
                                    return self
                                                   
                    except Exception as e:
                        self.title = "Cannot find title (API Down)"
                        self.author = "Cannot find author (API Down)"
                        return self

                # Get Covers 
                self.cover = await get_cover(session, self.isbn, "M")
            return self
        else:
            return self


    async def fetch_author(self, session: aiohttp.ClientSession, url: str):
        """Fetch author information from Open Library API"""
        try:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return None
                response_json = await response.json()
                return response_json
        except Exception as e:
            return None


    def __dict__(self):
        """Convert book object to dictionary"""
        return {
            "t": self.title,
            "a": self.author,
            "i": self.isbn,
            "c": self.cover,
            "h": self.hidden
        }
    
    def detailed(self):
        return self.__dict__()
    
    def concise(self):
        concise = {
            "i": self.isbn,
            "h": self.hidden
        }
        return concise