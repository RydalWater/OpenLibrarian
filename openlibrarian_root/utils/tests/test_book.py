from django.test import TestCase
from utils.Book import Book, get_cover
import aiohttp, requests, asyncio
from aioresponses import aioresponses
from unittest import IsolatedAsyncioTestCase

class BookUnitTest(TestCase):
    def setUp(self):
        pass

    def test_book_isbn(self):
        """
        Test book with valid ISBN
        """
        test_isbn_raw = "978-0-141-03058-6"
        test_isbn_clean = "9780141030586"
        
        book1 = Book(isbn=test_isbn_raw)
        self.assertEqual(book1.isbn, test_isbn_clean)
        self.assertEqual(book1.url, f"https://openlibrary.org/isbn/{test_isbn_clean}.json")
        self.assertEqual(book1.title, None)
        self.assertEqual(book1.author, None)
        self.assertEqual(book1.cover, None)
        self.assertEqual(book1.hidden, "N")

        book2 = Book(isbn=test_isbn_clean, hidden="Y")
        self.assertEqual(book2.isbn, "9780141030586")
        self.assertEqual(book2.url, f"https://openlibrary.org/isbn/{test_isbn_clean}.json")
        self.assertEqual(book2.title, None)
        self.assertEqual(book2.author, None)
        self.assertEqual(book2.cover, None)
        self.assertEqual(book2.hidden, "Y")

        book3 = Book(isbn=test_isbn_clean, hidden="N")
        self.assertEqual(book3.isbn, test_isbn_clean)
        self.assertEqual(book3.url, f"https://openlibrary.org/isbn/{test_isbn_clean}.json")
        self.assertEqual(book3.title, None)
        self.assertEqual(book3.author, None)
        self.assertEqual(book3.cover, None)
        self.assertEqual(book3.hidden, "N")
    
    def test_book_url(self):
        """
        Test book with valid URL
        """
        test_url = "https://openlibrary.org/isbn/9780141030586.json"
        book1 = Book(url=test_url)
        self.assertEqual(book1.isbn, "9780141030586")
        self.assertEqual(book1.url, test_url)
        self.assertEqual(book1.title, None)
        self.assertEqual(book1.author, None)
        self.assertEqual(book1.cover, None)
        self.assertEqual(book1.hidden, "N")

    def test_book_hidden(self):
        """
        Test book with hidden ISBN
        """
        book1 = Book(isbn="Hidden", hidden="Y")
        self.assertEqual(book1.isbn, "Hidden")
        self.assertEqual(book1.title, "Mysterious Book")
        self.assertEqual(book1.author, "Unknown Author")
        self.assertEqual(book1.cover, "M")
        self.assertEqual(book1.hidden, "Y")
    
    def test_book_dict(self):
        """
        Test book with valid dict
        """
        test_dict = {
            "i": "9780141030586",
            "t": "Old Ways",
            "a": "Robert Macfarlane",
            "c": "https://covers.openlibrary.org/b/isbn/9780141030586-S.jpg",
            "h": "N"
        }
        book1 = Book(dict=test_dict)
        self.assertEqual(book1.isbn, "9780141030586")
        self.assertEqual(book1.title, "Old Ways")
        self.assertEqual(book1.author, "Robert Macfarlane")
        self.assertEqual(book1.cover, "https://covers.openlibrary.org/b/isbn/9780141030586-S.jpg")
        self.assertEqual(book1.hidden, "N")
    
    def test_book_concise(self):
        """
        Test book with valid concise dict
        """
        test_dict = {
            "i": "9780141030586",
            "t": "Old Ways",
            "a": "Robert Macfarlane",
            "c": "https://covers.openlibrary.org/b/isbn/9780141030586-S.jpg",
            "h": "N"
        }
        book1 = Book(dict=test_dict)
        self.assertEqual(book1.concise(), {"i": "9780141030586", "h": "N"})

    async def test_get_cover(self):
        """
        Test get_cover
        """
        async with aiohttp.ClientSession() as session:
            cover = await get_cover(session,"9780141030586", "S")
            self.assertEqual(cover, "https://covers.openlibrary.org/b/isbn/9780141030586-S.jpg")
            cover = await get_cover(session,"9780141030586", "M")
            self.assertEqual(cover, "https://covers.openlibrary.org/b/isbn/9780141030586-M.jpg")
            cover = await get_cover(session,"9780141030586", "L")
            self.assertEqual(cover, "https://covers.openlibrary.org/b/isbn/9780141030586-L.jpg")
            cover = await get_cover(session,"9408466502123", "S")
            self.assertEqual(cover, "N")
    
    async def test_get_book_no_url(self):
        """
        Test get book with no URL
        """
        book1 = Book(isbn="9780141030586")
        book1.url = ""
        self.assertEqual(await book1.get_book(), book1)
    
    async def test_get_book_with_url(self):
        """
        Test get book with URL
        """
        book1 = await Book(isbn="9780141030586", hidden="Y").get_book()
        book1_dict = book1.__dict__()
        self.assertEqual(book1_dict["t"], "Old Ways")
        self.assertEqual(book1_dict["a"], "Robert Macfarlane")
        self.assertEqual(book1_dict["i"], "9780141030586")
        self.assertEqual(book1_dict["c"], "https://covers.openlibrary.org/b/isbn/9780141030586-M.jpg")
        self.assertEqual(book1_dict["h"], "Y")
        book1_detailed = book1.detailed()
        self.assertEqual(book1_dict, book1_detailed)

class TestBook(IsolatedAsyncioTestCase):
    async def test_timeout_exception_first_request(self):
        with aioresponses() as mocked:
            mocked.get('https://openlibrary.org/isbn/9780141030586.json', exception=asyncio.TimeoutError())
            book = Book(isbn='9780141030586')
            await book.get_book()
            self.assertEqual(book.title, "Cannot find title (API Down)")
            self.assertEqual(book.author, "Cannot find author (API Down)")
            self.assertIsNone(book.cover)

    async def test_timeout_exception_second_request(self):
        with aioresponses() as mocked:
            mocked.get('https://openlibrary.org/isbn/9780141030586.json', status=404)
            mocked.get('https://www.googleapis.com/books/v1/volumes?q=isbn:9780141030586', exception=asyncio.TimeoutError())
            book = Book(isbn='9780141030586')
            await book.get_book()
            self.assertEqual(book.title, "Cannot find title (API Down)")
            self.assertEqual(book.author, "Cannot find author (API Down)")
            self.assertIsNone(book.cover)

    async def test_successful_first_request(self):
        with aioresponses() as mocked:
            mocked.get('https://openlibrary.org/isbn/9780141030586.json', status=200, payload={"title": "To Kill a Mockingbird", "authors": [{"key": "/authors/JK_Rowling"}]})
            mocked.get('https://openlibrary.org/authors/JK_Rowling.json', status=200, payload={"name": "J.K. Rowling"})
            book = Book(isbn='9780141030586')
            await book.get_book()
            self.assertEqual(book.title, "To Kill a Mockingbird")
            self.assertEqual(book.author, "J.K. Rowling")
            self.assertIsNotNone(book.cover)

    async def test_successful_second_request(self):
        with aioresponses() as mocked:
            mocked.get('https://openlibrary.org/isbn/9780141030586.json', status=404)
            mocked.get('https://www.googleapis.com/books/v1/volumes?q=isbn:9780141030586', status=200, payload={"items": [{"volumeInfo": {"title": "Harry Potter and the Philosopher's Stone", "authors": ["J.K. Rowling"]}}]})
            book = Book(isbn='9780141030586')
            await book.get_book()
            self.assertEqual(book.title, "Harry Potter and the Philosopher's Stone")
            self.assertEqual(book.author, "J.K. Rowling")
            self.assertIsNotNone(book.cover)

    async def test_api_down(self):
        with aioresponses() as mocked:
            mocked.get('https://openlibrary.org/isbn/9780141030586.json', status=500)
            mocked.get('https://www.googleapis.com/books/v1/volumes?q=isbn:9780141030586', status=500)
            book = Book(isbn='9780141030586')
            await book.get_book()
            self.assertEqual(book.title, "Cannot find title (API Down)")
            self.assertEqual(book.author, "Cannot find author (API Down)")
            self.assertIsNone(book.cover)

    async def test_get_cover_api_down(self):
        """
        Test get_cover when the APIs are down
        """
        with aioresponses() as mocked:
            mocked.get('https://covers.openlibrary.org/b/isbn/9780141030586-S.jpg', status=500)
            mocked.get('https://covers.openlibrary.org/b/isbn/9780141030586-M.jpg', status=500)
            mocked.get('https://covers.openlibrary.org/b/isbn/9780141030586-L.jpg', status=500)
            mocked.get('https://www.googleapis.com/books/v1/volumes', status=500)
            async with aiohttp.ClientSession() as session:
                cover = await get_cover(session, "9780141030586", "S")
                self.assertEqual(cover, "N")
                cover = await get_cover(session, "9780141030586", "M")
                self.assertEqual(cover, "N")
                cover = await get_cover(session, "9780141030586", "L")
                self.assertEqual(cover, "N")
                cover = await get_cover(session, "9408466502123", "S")
                self.assertEqual(cover, "N")

    async def test_get_cover_alternative_success(self):
        """
        Test get_cover when the first try block fails and the second try block succeeds
        """
        with aioresponses() as mocked:
            # Mock the first try block to fail with a 404 status
            mocked.get('https://covers.openlibrary.org/b/isbn/9780141030586-S.jpg', status=404)
            
            # Mock the second try block to succeed with a 200 status and a valid response
            mocked.get('https://www.googleapis.com/books/v1/volumes?q=isbn:9780141030586', status=200, payload={
                "kind": "books#volumes",
                "totalItems": 1,
                "items": [
                    {
                        "volumeInfo": {
                            "imageLinks": {
                                "thumbnail": "http://books.google.com/books/content?id=T4eMEAAAQBAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api"
                            }
                        }
                    }
                ]
            })
            mocked.get('http://books.google.com/books/content?id=T4eMEAAAQBAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api', status=200)
            
            async with aiohttp.ClientSession() as session:
                cover = await get_cover(session, "9780141030586", "S")
                self.assertEqual(cover, "http://books.google.com/books/content?id=T4eMEAAAQBAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api")

    async def test_get_cover_alternative_failure(self):
        """
        Test get_cover when the first try block fails and the second try block fails
        """
        with aioresponses() as mocked:
            # Mock the first try block to fail with a 404 status
            mocked.get('https://covers.openlibrary.org/b/isbn/9780141030586-S.jpg', status=404)

            # Mock the second try block to succeed with a 200 status and a valid response
            mocked.get('https://www.googleapis.com/books/v1/volumes?q=isbn:9780141030586', status=200, payload={
                "kind": "books#volumes",
                "totalItems": 1,
                "items": [
                    {
                        "volumeInfo": {
                            "imageLinks": {
                                "thumbnail": "https://example.com/thumbnail.jpg"
                            }
                        }
                    }
                ]
            })
            # Mock the third try block to fail with a ClientError
            mocked.get('https://example.com/thumbnail.jpg', exception=aiohttp.ClientError())
            
            async with aiohttp.ClientSession() as session:
                cover = await get_cover(session, "9780141030586", "S")
                self.assertEqual(cover, "N")
    
    async def test_fetch_author_failed(self):
        """
        Test fetch_author when the API returns a response other than 200
        """
        test_book = Book(isbn="9780141030586")
        with aioresponses() as mocked:
            mocked.get('https://openlibrary.org/authors/OL7932235A.json', status=500)
            async with aiohttp.ClientSession() as session:
                author = await test_book.fetch_author(session, "https://openlibrary.org/authors/OL7932235A.json")
                self.assertEqual(author, None)
    
    async def test_fetch_author_timeout(self):
        """
        Test fetch_author when the API times out
        """
        test_book = Book(isbn="9780141030586")
        with aioresponses() as mocked:
            mocked.get('https://openlibrary.org/authors/OL7932235A.json', exception=asyncio.TimeoutError())
            async with aiohttp.ClientSession() as session:
                author = await test_book.fetch_author(session, "https://openlibrary.org/authors/OL7932235A.json")
                self.assertEqual(author, None)
    
    async def test_get_book_primary_noauthor(self):
        """
        Test get book where the first block returns a 200 response but the response.json does not contain "authors" in the keys
        """
        with aioresponses() as mocked:
            mocked.get('https://openlibrary.org/isbn/9780141030586.json', status=200, payload={"title": "To Kill a Mockingbird"})
            book = Book(isbn='9780141030586')
            await book.get_book()
            self.assertEqual(book.title, "To Kill a Mockingbird")
            self.assertEqual(book.author, "Unknown Author")
            self.assertEqual(book.cover ,"N")
    
    async def test_get_book_secondary_noauthor(self):
        """
        Test get book where the second block returns a 200 response but the response.json does not contain "authors" in the keys
        """
        with aioresponses() as mocked:
            mocked.get('https://openlibrary.org/isbn/9780141030586.json', status=404)
            mocked.get('https://www.googleapis.com/books/v1/volumes?q=isbn:9780141030586', status=200, payload={"items": [{"volumeInfo": {"title": "Harry Potter and the Philosopher's Stone"}}]})
            book = Book(isbn='9780141030586')
            await book.get_book()
            self.assertEqual(book.title, "Harry Potter and the Philosopher's Stone")
            self.assertEqual(book.author, "Cannot find author")
            self.assertEqual(book.cover ,"N")

    async def test_get_book_secondary_notitle(self):
        """
        Test get book where the second block returns a 200 response but the response.json does not contain "title" in the keys
        """
        with aioresponses() as mocked:
            mocked.get('https://openlibrary.org/isbn/9780141030586.json', status=404)
            mocked.get('https://www.googleapis.com/books/v1/volumes?q=isbn:9780141030586', status=200, payload={"items": [{"volumeInfo": {"authors": ["J.K. Rowling"]}}]})
            book = Book(isbn='9780141030586')
            await book.get_book()
            self.assertEqual(book.title, "Cannot find title")
            self.assertEqual(book.author, "J.K. Rowling")
            self.assertEqual(book.cover ,"N")
    
    async def test_api_invalid_json(self):
        """
        Test that the Book class handles invalid JSON responses from the API
        """
        with aioresponses() as mocked:
            mocked.get('https://openlibrary.org/isbn/9780141030586.json', status=200, body='Invalid JSON')
            book = Book(isbn='9780141030586')
            await book.get_book()
            self.assertEqual(book.title, "Cannot find title (API Down)")
            self.assertEqual(book.author, "Cannot find author (API Down)")

    async def test_api_missing_values(self):
        """
        Test that the Book class handles API responses with missing or null values
        """
        with aioresponses() as mocked:
            mocked.get('https://openlibrary.org/isbn/9780141030586.json', status=200, body='{"title": null, "authors": []}')
            book = Book(isbn='9780141030586')
            await book.get_book()
            self.assertEqual(book.title, "Cannot find title (API Down)")
            self.assertEqual(book.author, "Cannot find author (API Down)")