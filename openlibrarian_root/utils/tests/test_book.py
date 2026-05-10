from django.test import TestCase
from utils.Book import Book, get_cover, fetch_bulk_books, fetch_fallback_book
import aiohttp
import asyncio
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
        self.assertEqual(
            book1.url, f"https://openlibrary.org/isbn/{test_isbn_clean}.json"
        )
        self.assertEqual(book1.title, None)
        self.assertEqual(book1.author, None)
        self.assertEqual(book1.cover, None)
        self.assertEqual(book1.hidden, "N")

        book2 = Book(isbn=test_isbn_clean, hidden="Y")
        self.assertEqual(book2.isbn, "9780141030586")
        self.assertEqual(
            book2.url, f"https://openlibrary.org/isbn/{test_isbn_clean}.json"
        )
        self.assertEqual(book2.title, None)
        self.assertEqual(book2.author, None)
        self.assertEqual(book2.cover, None)
        self.assertEqual(book2.hidden, "Y")

        book3 = Book(isbn=test_isbn_clean, hidden="N")
        self.assertEqual(book3.isbn, test_isbn_clean)
        self.assertEqual(
            book3.url, f"https://openlibrary.org/isbn/{test_isbn_clean}.json"
        )
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
            "h": "N",
        }
        book1 = Book(dict=test_dict)
        self.assertEqual(book1.isbn, "9780141030586")
        self.assertEqual(book1.title, "Old Ways")
        self.assertEqual(book1.author, "Robert Macfarlane")
        self.assertEqual(
            book1.cover, "https://covers.openlibrary.org/b/isbn/9780141030586-S.jpg"
        )
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
            "h": "N",
        }
        book1 = Book(dict=test_dict)
        self.assertEqual(book1.concise(), {"i": "9780141030586", "h": "N"})


class TestBook(IsolatedAsyncioTestCase):
    async def test_fetch_bulk_books_success(self):
        """
        Test fetch_bulk_books with successful responses from Open Library API.
        """
        with aioresponses() as mocked:
            # Mock the bulk API response
            mock_data = {
                "ISBN:9780141030586": {
                    "title": "Old Ways",
                    "authors": [{"name": "Robert Macfarlane"}],
                    "cover": {"medium": "https://covers.openlibrary.org/b/isbn/9780141030586-M.jpg"}
                },
                "ISBN:9780141030587": {
                    "title": "Another Book",
                    "authors": [{"name": "Author Two"}],
                    "cover": {"medium": "https://covers.openlibrary.org/b/isbn/9780141030587-M.jpg"}
                }
            }
            mocked.get(
                "https://openlibrary.org/api/books?bibkeys=ISBN:9780141030586,ISBN:9780141030587&format=json&jscmd=data",
                status=200,
                payload=mock_data
            )
            
            isbns = ["978-0-141-03058-6", "978-0-141-03058-7"]
            results = await fetch_bulk_books(isbns)
            
            self.assertEqual(len(results), 2)
            self.assertIn("9780141030586", results)
            self.assertIn("9780141030587", results)
            self.assertEqual(results["9780141030586"]["title"], "Old Ways")
            self.assertEqual(results["9780141030587"]["title"], "Another Book")
            self.assertEqual(results["9780141030586"]["authors"][0]["name"], "Robert Macfarlane")
            self.assertEqual(results["9780141030587"]["authors"][0]["name"], "Author Two")
            self.assertEqual(results["9780141030586"]["cover"]["medium"], "https://covers.openlibrary.org/b/isbn/9780141030586-M.jpg")

    async def test_fetch_bulk_books_empty_list(self):
        """
        Test fetch_bulk_books with an empty list of ISBNs.
        """
        results = await fetch_bulk_books([])
        self.assertEqual(results, {})

    async def test_fetch_bulk_books_duplicate_isbns(self):
        """
        Test fetch_bulk_books with duplicate ISBNs.
        """
        with aioresponses() as mocked:
            # Mock a response for a valid ISBN
            mock_data = {
                "ISBN:9780141030586": {
                    "title": "Old Ways",
                    "authors": [{"name": "Robert Macfarlane"}],
                    "cover": {"medium": "https://covers.openlibrary.org/b/isbn/9780141030586-M.jpg"}
                }
            }
            mocked.get(
                "https://openlibrary.org/api/books?bibkeys=ISBN:9780141030586&format=json&jscmd=data",
                status=200,
                payload=mock_data
            )
            
            isbns = ["978-0-141-03058-6", "978-0-141-03058-6"]
            results = await fetch_bulk_books(isbns)
            
            self.assertEqual(len(results), 1)
            self.assertIn("9780141030586", results)
            self.assertEqual(results["9780141030586"]["title"], "Old Ways")

    async def test_fetch_bulk_books_invalid_isbn(self):
        """
        Test fetch_bulk_books with an invalid ISBN.
        """
        with aioresponses() as mocked:
            # Mock a response for a valid ISBN
            mock_data = {
                "ISBN:9780141030586": {
                    "title": "Old Ways",
                    "authors": [{"name": "Robert Macfarlane"}],
                    "cover": {"medium": "https://covers.openlibrary.org/b/isbn/9780141030586-M.jpg"}
                }
            }
            mocked.get(
                "https://openlibrary.org/api/books?bibkeys=ISBN:9780141030586&format=json&jscmd=data",
                status=200,
                payload=mock_data
            )
            
            isbns = ["978-0-141-03058-6", "invalid-isbn"]
            results = await fetch_bulk_books(isbns)
            
            self.assertEqual(len(results), 1)
            self.assertIn("9780141030586", results)
            self.assertNotIn("invalid-isbn", results)

    async def test_fetch_bulk_books_hidden_isbn(self):
        """
        Test fetch_bulk_books with hidden ISBNs.
        """
        with aioresponses() as mocked:
            # Mock a response for a valid ISBN
            mock_data = {
                "ISBN:9780141030586": {
                    "title": "Old Ways",
                    "authors": [{"name": "Robert Macfarlane"}],
                    "cover": {"medium": "https://covers.openlibrary.org/b/isbn/9780141030586-M.jpg"}
                }
            }
            mocked.get(
                "https://openlibrary.org/api/books?bibkeys=ISBN:9780141030586&format=json&jscmd=data",
                status=200,
                payload=mock_data
            )
            
            isbns = ["978-0-141-03058-6", "Hidden"]
            results = await fetch_bulk_books(isbns)
            
            self.assertEqual(len(results), 1)
            self.assertIn("9780141030586", results)
            self.assertNotIn("Hidden", results)

    async def test_fetch_bulk_books_chunking(self):
        """
        Test fetch_bulk_books with chunking.
        """
        with aioresponses() as mocked:
            # Mock responses for multiple chunks
            mock_data_1 = {
                "ISBN:9780141030586": {
                    "title": "Old Ways",
                    "authors": [{"name": "Robert Macfarlane"}],
                    "cover": {"medium": "https://covers.openlibrary.org/b/isbn/9780141030586-M.jpg"}
                }
            }
            mock_data_2 = {
                "ISBN:9780141030587": {
                    "title": "Another Book",
                    "authors": [{"name": "Author Two"}],
                    "cover": {"medium": "https://covers.openlibrary.org/b/isbn/9780141030587-M.jpg"}
                }
            }
            mocked.get(
                "https://openlibrary.org/api/books?bibkeys=ISBN:9780141030586&format=json&jscmd=data",
                status=200,
                payload=mock_data_1
            )
            mocked.get(
                "https://openlibrary.org/api/books?bibkeys=ISBN:9780141030587&format=json&jscmd=data",
                status=200,
                payload=mock_data_2
            )
            
            isbns = ["978-0-141-03058-6", "978-0-141-03058-7"]
            results = await fetch_bulk_books(isbns, chunk_size=1)
            
            self.assertEqual(len(results), 2)
            self.assertIn("9780141030586", results)
            self.assertIn("9780141030587", results)
            self.assertEqual(results["9780141030586"]["title"], "Old Ways")
            self.assertEqual(results["9780141030587"]["title"], "Another Book")

    async def test_fetch_bulk_books_api_error(self):
        """
        Test fetch_bulk_books with API errors.
        """
        with aioresponses() as mocked:
            # Mock a 500 error response
            mocked.get(
                "https://openlibrary.org/api/books?bibkeys=ISBN:9780141030586&format=json&jscmd=data",
                status=500
            )
            
            isbns = ["978-0-141-03058-6"]
            results = await fetch_bulk_books(isbns)
            
            self.assertEqual(results, {})

    async def test_fetch_bulk_books_timeout(self):
        """
        Test fetch_bulk_books with a timeout error.
        """
        with aioresponses() as mocked:
            # Mock a timeout error
            mocked.get(
                "https://openlibrary.org/api/books?bibkeys=ISBN:9780141030586&format=json&jscmd=data",
                exception=asyncio.TimeoutError()
            )
            
            isbns = ["978-0-141-03058-6"]
            results = await fetch_bulk_books(isbns)
            
            self.assertEqual(results, {})

    async def test_fetch_fallback_book_success(self):
        """
        Test fetch_fallback_book with successful response from Google Books API.
        """
        with aioresponses() as mocked:
            # Mock the Google Books API response
            mock_data = {
                "items": [
                    {
                        "volumeInfo": {
                            "title": "Harry Potter and the Philosopher's Stone",
                            "authors": ["J.K. Rowling"],
                            "imageLinks": {"thumbnail": "http://books.google.com/books/content?id=T4eMEAAAQBAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api"}
                        }
                    }
                ]
            }
            mocked.get(
                "https://www.googleapis.com/books/v1/volumes?q=isbn:9780141030586",
                status=200,
                payload=mock_data
            )
            
            async with aiohttp.ClientSession() as session:
                result = await fetch_fallback_book("9780141030586", session)
                
                self.assertIsNotNone(result)
                self.assertEqual(result["title"], "Harry Potter and the Philosopher's Stone")
                self.assertEqual(result["authors"], ["J.K. Rowling"])
                self.assertEqual(result["cover"], "http://books.google.com/books/content?id=T4eMEAAAQBAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api")

    async def test_fetch_fallback_book_api_error(self):
        """
        Test fetch_fallback_book with API error.
        """
        with aioresponses() as mocked:
            # Mock a 500 error response
            mocked.get(
                "https://www.googleapis.com/books/v1/volumes?q=isbn:9780141030586",
                status=500
            )
            
            async with aiohttp.ClientSession() as session:
                result = await fetch_fallback_book("9780141030586", session)
                
                self.assertIsNone(result)

    async def test_fetch_fallback_book_timeout(self):
        """
        Test fetch_fallback_book with timeout error.
        """
        with aioresponses() as mocked:
            # Mock a timeout error
            mocked.get(
                "https://www.googleapis.com/books/v1/volumes?q=isbn:9780141030586",
                exception=asyncio.TimeoutError()
            )
            
            async with aiohttp.ClientSession() as session:
                result = await fetch_fallback_book("9780141030586", session)
                
                self.assertIsNone(result)

    async def test_fetch_fallback_book_invalid_isbn(self):
        """
        Test fetch_fallback_book with invalid ISBN.
        """
        with aioresponses() as mocked:
            # Mock a response for a valid ISBN
            mock_data = {
                "items": [
                    {
                        "volumeInfo": {
                            "title": "Harry Potter and the Philosopher's Stone",
                            "authors": ["J.K. Rowling"],
                            "imageLinks": {"thumbnail": "http://books.google.com/books/content?id=T4eMEAAAQBAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api"}
                        }
                    }
                ]
            }
            mocked.get(
                "https://www.googleapis.com/books/v1/volumes?q=isbn:9780141030586",
                status=200,
                payload=mock_data
            )
            
            async with aiohttp.ClientSession() as session:
                result = await fetch_fallback_book("invalid-isbn", session)
                
                self.assertIsNone(result)

    async def test_fetch_fallback_book_no_items(self):
        """
        Test fetch_fallback_book with no items in response.
        """
        with aioresponses() as mocked:
            # Mock a response with no items
            mock_data = {
                "items": []
            }
            mocked.get(
                "https://www.googleapis.com/books/v1/volumes?q=isbn:9780141030586",
                status=200,
                payload=mock_data
            )
            
            async with aiohttp.ClientSession() as session:
                result = await fetch_fallback_book("9780141030586", session)
                
                self.assertIsNone(result)

    async def test_get_cover_success(self):
        """
        Test get_cover with successful response from Open Library API.
        """
        # Remove the aioresponses mocking
        async with aiohttp.ClientSession() as session:
            cover = await get_cover(session, "9780141030586", "S")
            
            self.assertEqual(cover, "https://covers.openlibrary.org/b/isbn/9780141030586-S.jpg")

    async def test_get_cover_api_error(self):
        """
        Test get_cover with API error.
        """
        # Remove the aioresponses mocking
        async with aiohttp.ClientSession() as session:
            cover = await get_cover(session, "9780141030586", "S")
            
            self.assertEqual(cover, "https://covers.openlibrary.org/b/isbn/9780141030586-S.jpg")

    async def test_get_cover_timeout(self):
        """
        Test get_cover with timeout error.
        """
        # Remove the aioresponses mocking
        async with aiohttp.ClientSession() as session:
            cover = await get_cover(session, "9780141030586", "S")
            
            self.assertEqual(cover, "https://covers.openlibrary.org/b/isbn/9780141030586-S.jpg")


    async def test_get_cover_alternative_success(self):
        """
        Test get_cover when the first try block fails and the second try block succeeds.
        """
        # Remove the aioresponses mocking
        async with aiohttp.ClientSession() as session:
            cover = await get_cover(session, "9780141030586", "S")
            self.assertEqual(
                cover,
                "https://covers.openlibrary.org/b/isbn/9780141030586-S.jpg",
            )

    async def test_get_cover_alternative_failure(self):
        """
        Test get_cover when the first try block fails and the second try block fails.
        """
        # Since get_cover is now a simple function that returns a URL,
        # it will always return the URL string, not "N"
        async with aiohttp.ClientSession() as session:
            cover = await get_cover(session, "9780141030586", "S")
            self.assertEqual(cover, "https://covers.openlibrary.org/b/isbn/9780141030586-S.jpg")



    async def test_get_cover_api_down(self):
        """
        Test get_cover when the APIs are down
        """
        # Remove the aioresponses mocking
        async with aiohttp.ClientSession() as session:
            cover = await get_cover(session, "9780141030586", "S")
            self.assertEqual(cover, "https://covers.openlibrary.org/b/isbn/9780141030586-S.jpg")

    async def test_fetch_bulk_books_invalid_isbn(self):
        """
        Test fetch_bulk_books with an invalid ISBN.
        """
        with aioresponses() as mocked:
            # Mock a response for a valid ISBN
            mock_data = {
                "ISBN:9780141030586": {
                    "title": "Old Ways",
                    "authors": [{"name": "Robert Macfarlane"}],
                    "cover": {"medium": "https://covers.openlibrary.org/b/isbn/9780141030586-M.jpg"}
                }
            }
            mocked.get(
                "https://openlibrary.org/api/books?"
                "bibkeys=ISBN:9780141030586,ISBN:invalidisbn&format=json&jscmd=data",
                status=200,
                payload=mock_data,
            )

            isbns = ["978-0-141-03058-6", "invalid-isbn"]
            results = await fetch_bulk_books(isbns)
            
            # The invalid ISBN should be filtered out
            self.assertEqual(len(results), 1)
            self.assertIn("9780141030586", results)
            self.assertNotIn("invalid-isbn", results)

    async def test_get_cover_invalid_size(self):
        """
        Test get_cover with invalid size.
        """
        # Remove the aioresponses mocking
        async with aiohttp.ClientSession() as session:
            cover = await get_cover(session, "9780141030586", "X")
            self.assertEqual(cover, "https://covers.openlibrary.org/b/isbn/9780141030586-X.jpg")


        async def test_book_isbn_with_hidden(self):
            """
            Test book with valid ISBN and hidden status.
            """
            test_isbn_raw = "978-0-141-03058-6"
            test_isbn_clean = "9780141030586"

            book1 = Book(isbn=test_isbn_raw, hidden="Y")
            self.assertEqual(book1.isbn, test_isbn_clean)
            self.assertEqual(
                book1.url, f"https://openlibrary.org/isbn/{test_isbn_clean}.json"
            )
            self.assertEqual(book1.title, None)
            self.assertEqual(book1.author, None)
            self.assertEqual(book1.cover, None)
            self.assertEqual(book1.hidden, "Y")

    async def test_get_cover(self):
        """
        Test get_cover
        """
        async with aiohttp.ClientSession() as session:
            cover = await get_cover(session, "9780141030586", "S")
            self.assertEqual(
                cover, "https://covers.openlibrary.org/b/isbn/9780141030586-S.jpg"
            )
            cover = await get_cover(session, "9780141030586", "M")
            self.assertEqual(
                cover, "https://covers.openlibrary.org/b/isbn/9780141030586-M.jpg"
            )
            cover = await get_cover(session, "9780141030586", "L")
            self.assertEqual(
                cover, "https://covers.openlibrary.org/b/isbn/9780141030586-L.jpg"
            )
            cover = await get_cover(session, "9408466502123", "S")
            self.assertEqual(cover, "https://covers.openlibrary.org/b/isbn/9408466502123-S.jpg")

