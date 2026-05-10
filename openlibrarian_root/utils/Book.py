import aiohttp
import asyncio
import os
from typing import Optional

BULK_API_URL = "https://openlibrary.org/api/books"
alt_api_url = "https://www.googleapis.com/books/v1/volumes"

email_address = os.getenv("EMAIL_ADDY", "")

headers = {
    "User-Agent": f"Open Librarian (A FOSS book tracker powered by Nostr) - {email_address}",
}


async def get_cover(session: aiohttp.ClientSession, isbn: str, size: str):
    """
    Backwards-compatible cover helper.
    Returns the deterministic Open Library cover URL without making HTTP requests.
    (OpenLibrary.py still imports this; update it later to skip the await.)
    """
    if not isbn or isbn == "N" or "Hidden" in isbn:
        return "N"
    return f"https://covers.openlibrary.org/b/isbn/{isbn}-{size}.jpg"


async def fetch_bulk_books(
    isbns: list[str],
    session: Optional[aiohttp.ClientSession] = None,
    chunk_size: int = 50,
) -> dict[str, dict]:
    """
    Fetch multiple books from Open Library bulk API.
    Returns {normalized_isbn: book_data}
    """
    if not isbns:
        return {}

    seen = set()
    unique_isbns = []
    for raw in isbns:
        norm = "".join(raw.split("-"))
        if norm not in seen and "Hidden" not in norm:
            seen.add(norm)
            unique_isbns.append(norm)

    results = {}
    owned_session = session is None
    if owned_session:
        timeout = aiohttp.ClientTimeout(total=20)
        session = aiohttp.ClientSession(headers=headers, timeout=timeout)

    try:
        for i in range(0, len(unique_isbns), chunk_size):
            chunk = unique_isbns[i : i + chunk_size]
            bibkeys = ",".join(f"ISBN:{isbn}" for isbn in chunk)
            url = f"{BULK_API_URL}?bibkeys={bibkeys}&format=json&jscmd=data"
            
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        for key, book_data in data.items():
                            isbn = key.replace("ISBN:", "")
                            results[isbn] = book_data
                        await asyncio.sleep(0.35)  # Be nice to the API and avoid hitting rate limits
            except (aiohttp.ClientError, asyncio.TimeoutError):
                continue
    finally:
        if owned_session:
            await session.close()

    return results

async def fetch_fallback_book(isbn: str, session: aiohttp.ClientSession) -> Optional[dict]:
    """Fallback to Google Books API for a single ISBN."""
    try:
        async with session.get(
            alt_api_url, params={"q": f"isbn:{isbn}"}, timeout=10
        ) as response:
            if response.status != 200:
                return None
            data = await response.json()
            items = data.get("items", [])
            if not items:
                return None
            info = items[0].get("volumeInfo", {})
            return {
                "title": info.get("title"),
                "authors": info.get("authors", []),
                "cover": info.get("imageLinks", {}).get("thumbnail", "N"),
            }
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return None


class Book:
    """
    Book Class. Allows for easy creation and access of book objects.
    """

    def __init__(self, **kwargs):
        """Initialize book object"""
        if "dict" in kwargs:
            d = kwargs["dict"]
            self.isbn = d["i"]
            self.url = f"https://openlibrary.org/isbn/{self.isbn}.json"
            self.title = d["t"]
            self.author = d["a"]
            self.cover = d["c"]
            self.hidden = d["h"]
            return

        if "isbn" in kwargs:
            self.isbn = "".join(kwargs["isbn"].split("-"))
            if "Hidden" in self.isbn:
                self.url = ""
            else:
                self.url = f"https://openlibrary.org/isbn/{self.isbn}.json"
        elif "url" in kwargs:
            self.isbn = kwargs["url"].split("/")[4].split(".")[0]
            self.url = kwargs["url"]
        else:
            self.isbn = ""
            self.url = ""

        self.hidden = kwargs.get("hidden", "N")

        if "Hidden" in self.isbn:
            self.title = "Mysterious Book"
            self.author = "Unknown Author"
            self.cover = "M"
        else:
            self.title = kwargs.get("title")
            self.author = kwargs.get("author")
            self.cover = kwargs.get("cover")

    @classmethod
    def from_bulk_data(cls, isbn: str, data: dict, hidden: str = "N") -> "Book":
        """
        Create a Book from Open Library bulk API data.
        """
        authors = data.get("authors", [])
        author_names = [a["name"] for a in authors if a.get("name")]
        author_str = ", ".join(author_names) if author_names else "Unknown Author"

        cover_data = data.get("cover")
        if isinstance(cover_data, dict):
            cover = (
                cover_data.get("medium")
                or cover_data.get("large")
                or cover_data.get("small", "N")
            )
        else:
            cover = "N"

        instance = cls(
            isbn=isbn,
            title=data.get("title"),
            author=author_str,
            cover=cover,
            hidden=hidden,
        )
        instance.url = data.get("url") or f"https://openlibrary.org/isbn/{isbn}.json"
        return instance

    @classmethod
    def placeholder(cls, isbn: str, hidden: str = "N") -> "Book":
        """Return a book with fallback/error text."""
        return cls(
            isbn=isbn,
            title="Cannot find title",
            author="Cannot find author",
            cover="N",
            hidden=hidden,
        )

    def __dict__(self):
        """Convert book object to dictionary"""
        return {
            "t": self.title,
            "a": self.author,
            "i": self.isbn,
            "c": self.cover,
            "h": self.hidden,
        }

    def detailed(self):
        return self.__dict__()

    def concise(self):
        return {"i": self.isbn, "h": self.hidden}
