import aiohttp, asyncio, os

api_url = "https://openlibrary.org/search.json"
alt_api_url = "https://www.googleapis.com/books/v1/volumes"

email_address = os.getenv("EMAIL_ADDY")

headers = {
    "User-Agent": f"Open Librarian (A FOSS book tracker powered by Nostr) - {email_address}",
}

async def get_cover(session: aiohttp.ClientSession, isbn: str, size: str):
    """Get cover image from Open Library API"""
    image = f"https://covers.openlibrary.org/b/isbn/{isbn}-{size}.jpg"
    async with session.get(image) as response:
        if "content-type" in response.headers:
            return image 
        else:
            response = await session.get(alt_api_url, params={"q": "isbn:" + isbn})
            if response.status != 200:
                return "N"
            else:
                data = await response.json()
                if "items" in data and "imageLinks" in data["items"][0]["volumeInfo"]:
                    image = data["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
                    async with session.get(image) as response:
                        if "content-type" in response.headers:
                            return image
                        else:
                            return "N"
                else:
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
                    try:
                        async with session.get(self.url, headers=headers) as response:
                            if response.status == 200:
                                response_json = await response.json()
                                self.title = response_json["title"]
            
                                if "authors" in response_json:
                                    author_urls = [f"https://openlibrary.org{author['key']}.json" for author in response_json["authors"] if author.get('key')]
                                    author_responses = await asyncio.gather(*[self.fetch_author(session, url) for url in author_urls])
            
                                    authors = [author["name"] for author in author_responses if author]
                                    self.author = ", ".join(authors)
                                else:
                                    self.author = "Unknown Author"
                            else:
                                alt_api = True
                                alt_url = f"{alt_api_url}?q=isbn:{self.isbn}"
                        if alt_api:
                            async with session.get(alt_url, headers=headers) as response:
                                if response.status == 200:
                                    response_json = await response.json()
                                    self.title = response_json["items"][0]["volumeInfo"]["title"]
                                    authors = [author for author in response_json["items"][0]["volumeInfo"]["authors"]]
                                    self.author = ", ".join(authors)
                                    if self.author == None:
                                        self.author = "Cannot find author"
                                    if self.title == None:
                                        self.title = "Cannot find title"
                                else:
                                    print(f"Error: {response.status} with ISBN: {self.isbn}")
                                    return self
        

                        self.cover = await get_cover(session, self.isbn, "M")
        
                    except Exception as e:
                        print(self.isbn)
                        print(f"An error occurred: {e}")            
            return self
        else:
            return self


    async def fetch_author(self, session: aiohttp.ClientSession, url: str):
        """Fetch author information from Open Library API"""
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                print(f"Error: {response.status} with author URL: {url}")
                return None
    
            response_json = await response.json()
            return response_json


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