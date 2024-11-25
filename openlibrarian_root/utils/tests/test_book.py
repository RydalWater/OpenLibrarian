from django.test import TestCase
from utils.Book import Book, get_cover
import aiohttp, requests

class BookUnitTest(TestCase):
    def setUp(self):
        pass

    def test_book_isbn(self):
        """
        Test book with valid ISBN
        """
        test_isbn_raw = "978-0-141-03058-6"
        test_isbn_clean = "9780141030586"
        response = requests.get(f"https://openlibrary.org/isbn/{test_isbn_clean}.json")
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