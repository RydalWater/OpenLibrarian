import aiohttp
import asyncio
import os
import re
import socket
from utils.Book import get_cover


api_url = "https://openlibrary.org/search.json"


email_address = os.getenv("EMAIL_ADDY")


headers = {
    "User-Agent": f"Open Librarian (A FOSS book tracker powered by Nostr) - {email_address}",
}


MAX_RETRIES = 3


async def _http_get_with_retry(session, url: str, params: dict):
    """GET with retry on transient failures (network errors, timeouts).

    Returns the parsed JSON body on success, or None on failure.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with session.get(url, headers=headers, params=params, timeout=30) as response:
                if response.status != 200:
                    print(f"[search] API returned status {response.status}")
                    if attempt == MAX_RETRIES:
                        return None
                    continue
                return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"[search] Attempt {attempt}/{MAX_RETRIES} failed for {url}: {e}")
            if attempt == MAX_RETRIES:
                return None

    return None


async def search_books(**kwargs):
    """Search for Books using Open Library API (with retry on network failure)."""
    param_tags = {
        "author": "author",
        "sort": "sort",
        "title": "title",
        "isbn": "isbn",
        "general": "q",
        "page": "page",
        "lang": "lang",
    }

    params = {}
    for key, value in kwargs.items():
        if key in param_tags:
            params[param_tags[key]] = str(value) if value is not None else ""

    # Add fields parameter (default is title,author_name,isbn,publish_date,number_of_pages_median,ratings_average,has_fulltext,cover_i) and limit (default is 20)
    if "fields" not in params:
        params["fields"] = (
            "title,author_name,isbn,publish_date,number_of_pages_median,ratings_average,has_fulltext,cover_i"
        )
    if "limit" not in params:
        params["limit"] = 20

    # Handle ISBN search specially - use bibkeys API for exact ISBN lookup
    isbn_search = kwargs.get("isbn")
    if isbn_search:
        clean_isbn = "".join(isbn_search.split("-"))
        connector = aiohttp.TCPConnector(family=socket.AF_INET)
        async with aiohttp.ClientSession(connector=connector) as session:
            # Use bibkeys API for ISBN lookups (faster, returns structured data)
            bib_url = "https://openlibrary.org/api/books"
            bib_params = {
                "bibkeys": f"ISBN:{clean_isbn}",
                "format": "json",
                "jscmd": "data"
            }
            response_json = await _http_get_with_retry(session, bib_url, bib_params)
            if response_json is None:
                print("[search] ISBN lookup failed after retries.")
                return None, None

            # bibkeys API returns dict like {"ISBN:...": {...book data...}}
            book_data = response_json.get(f"ISBN:{clean_isbn}", {})
            print(f"[search] ISBN lookup found keys: {list(book_data.keys()) if book_data else 'empty'}")

            if not book_data:
                print("[search] No books found for ISBN.")
                return 0, []

            # Return single book result in same format as search results
            title = book_data.get("title", "Unknown Title")
            author_list = book_data.get("authors", [])
            author_name = ", ".join([auth["name"] for auth in author_list]) if author_list else ""

            isbn_13s = book_data.get("identifiers", {}).get("isbn_13", [])
            isbn_list = list(dict.fromkeys(isbn_13s)) if isinstance(isbn_13s, list) else [isbn_13s]
            isbns_flat = isbn_list[0] if len(isbn_list) == 1 else "Multiple ISBNs"

            publish_date = book_data.get("publish_date", "")
            number_of_pages = book_data.get("number_of_pages")
            ratings = book_data.get("ratings_count", 0)
            has_fulltext = "Y" if (book_data.get("fulltext") or book_data.get("preview_url")) else "N"
            cover = book_data.get("cover_i")

            return 1, [{
                "title": title,
                "author_name": author_name,
                "isbn": isbns_flat,
                "isbns_m": isbn_list,
                "publish_date": publish_date,
                "number_of_pages_median": number_of_pages,
                "ratings_average": ratings if ratings > 0 else None,
                "has_fulltext": has_fulltext,
                "cover": f"https://covers.openlibrary.org/b/id/{cover}-M.jpg" if cover else "N",
            }]

    # FORCE IPv4 ONLY to bypass aiohappyeyeballs and IPv6 routing issues
    connector = aiohttp.TCPConnector(family=socket.AF_INET)
    async with aiohttp.ClientSession(connector=connector) as session:
        response_json = await _http_get_with_retry(session, api_url, params)
        if response_json is None:
            return None, None

        # If there are no results
        if not response_json or "docs" not in response_json or len(response_json.get("docs", [])) == 0:
            print("[search] No books found.")
            return 0, []

        # If there are results
        docs = response_json["docs"]
        num_results = response_json.get("numFound", len(docs))

        # List of tasks to gather covers concurrently
        if "isbn" in params.keys() and isbn_search:
            cover_tasks = [get_cover(session, str(isbn_search), "M")]
        else:
            cover_tasks = []

        # Gather all cover tasks concurrently
        if cover_tasks:
            covers = await asyncio.gather(*cover_tasks)
        else:
            covers = ["N"]  # No cover data for non-ISBN searches (API doesn't return by default)

        # Construct results with gathered cover data
        results = []
        for doc in docs:
            title = doc.get("title", "")
            author_names = doc.get("author_name", [])
            author_name = ", ".join(author_names) if author_names else ""

            # Get ISBN - check multiple sources: isbn field, identifiers.isbn_13, or ia keys
            isbn_list = []

            # Try isbn field first (for non-ISBN searches)
            existing_isbn_field = doc.get("isbn", [])
            if existing_isbn_field and len(existing_isbn_field) > 0:
                isbn_list.extend(existing_isbn_field)

            # Try identifiers.isbn_13 field
            identifiers = doc.get("identifiers", {})
            isbn_13s = identifiers.get("isbn_13", [])
            if isbn_13s and len(isbn_13s) > 0:
                isbn_list.extend(isbn_13s)

            # If still no ISBN, extract from ia keys (scattered format like "isbn_978...")
            if not isbn_list and "ia" in doc:
                ia_keys = doc.get("ia", [])
                for ia_key in ia_keys:
                    if isinstance(ia_key, str):
                        # Look for ISBN patterns in IA keys
                        isbn_match = re.search(r'isbn_(978\d+)', ia_key)
                        if isbn_match:
                            isbn_list.append(isbn_match.group(1))

            # Deduplicate while preserving order
            isbn_list = list(dict.fromkeys(isbn_list))

            # Use search parameter when available (for ISBN searches)
            if "isbn" in params.keys() and isbn_search:
                isbn = str(isbn_search)
            elif len(isbn_list) == 1:
                isbn = isbn_list[0]
            elif len(isbn_list) > 1:
                isbn = "Multiple ISBNs"
            else:
                isbn = ""

            publish_date = doc.get("publish_date")
            if isinstance(publish_date, list):
                publish_date = publish_date[0] if publish_date else None
            has_fulltext = "Y" if doc.get("has_fulltext") else "N"
            number_of_pages_median = doc.get("number_of_pages_median")
            ratings_average = doc.get("ratings_average")
            cover_i = doc.get("cover_i")
            cover = f"https://covers.openlibrary.org/b/id/{cover_i}-M.jpg" if cover_i else "N"

            results.append(
                {
                    "title": title,
                    "author_name": author_name,
                    "isbn": isbn,
                    "isbns_m": isbn_list,
                    "publish_date": publish_date,
                    "number_of_pages_median": number_of_pages_median,
                    "ratings_average": ratings_average,
                    "has_fulltext": has_fulltext,
                    "cover": cover,
                }
            )

        return num_results, results