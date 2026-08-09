import aiohttp
import asyncio
import json
import os
import socket
from utils.Book import get_cover


API_URL = "https://openlibrary.org/search.json"

# Build a descriptive User-Agent. OpenLibrary asks clients to identify themselves.
_email = os.getenv("EMAIL_ADDY")
_contact = f" - {_email}" if _email else ""
HEADERS = {
    "User-Agent": f"Open Librarian (A FOSS book tracker powered by Nostr){_contact}",
    "Accept": "application/json",
}

MAX_RETRIES = 3


async def _http_get_with_retry(session: aiohttp.ClientSession, url: str, params: dict):
    """
    GET with retry on transient network failures.
    Returns parsed JSON or raises on persistent failure.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # We read the body inside the context manager so the connection is
            # cleanly released back to the pool before we return.
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                text = await response.text()
                if not text:
                    return None
                return json.loads(text)

        except (aiohttp.ClientError, json.JSONDecodeError) as e:
            print(f"[search] Attempt {attempt}/{MAX_RETRIES} failed for {url}: {e}")
            if attempt == MAX_RETRIES:
                raise
            # Brief backoff before retrying
            await asyncio.sleep(1)

    # Should never be reached
    raise aiohttp.ClientError("Unexpected retry path")


async def search_books(**kwargs):
    """
    Search for Books using the Open Library API (with retry on network failure).
    """
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
            params[param_tags[key]] = value

    # Default fields and limit
    if "fields" not in params:
        params["fields"] = (
            "title,author_name,isbn,publish_date,number_of_pages_median,"
            "ratings_average,has_fulltext"
        )
    if "limit" not in params:
        params["limit"] = 20

    # FORCE IPv4 ONLY to bypass aiohappyeyeballs / broken IPv6 routing,
    # and give the heavier search endpoint a generous timeout.
    connector = aiohttp.TCPConnector(family=socket.AF_INET)
    timeout = aiohttp.ClientTimeout(total=30, sock_connect=10, sock_read=20)

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers=HEADERS,
    ) as session:
        try:
            response_json = await _http_get_with_retry(session, API_URL, params)
        except aiohttp.ClientError as e:
            print(f"[search] API request failed after retries: {e}")
            return None, None

        # Empty body or no results
        if not response_json:
            print("[search] Empty response from API.")
            return 0, []

        num_found = response_json.get("numFound", 0)
        if num_found == 0:
            print("[search] No books found.")
            return 0, []

        docs = response_json.get("docs", [])

        # Filter documents with required keys
        valid_docs = [
            doc for doc in docs
            if doc.get("author_name") and doc.get("isbn")
        ]

        if not valid_docs:
            print("[search] No valid documents after filtering.")
            return 0, []

        # Gather covers concurrently
        if "isbn" in params:
            cover_tasks = [get_cover(session, params["isbn"], "M")]
        else:
            cover_tasks = [
                get_cover(session, doc["isbn"][0], "M")
                for doc in valid_docs
            ]

        covers = await asyncio.gather(*cover_tasks)

        # Build results
        results = []
        for doc, cover in zip(valid_docs, covers):
            title = doc["title"]
            author_name = ", ".join(doc["author_name"])

            if "isbn" in params:
                isbn = params["isbn"]
            elif len(doc["isbn"]) == 1:
                isbn = doc["isbn"][0]
            else:
                isbn = "Multiple ISBNs"

            isbns = doc["isbn"]
            publish_date = doc.get("publish_date", [None])[0]
            has_fulltext = doc.get("has_fulltext", False)
            number_of_pages_median = doc.get("number_of_pages_median")
            ratings_average = doc.get("ratings_average")

            results.append(
                {
                    "title": title,
                    "author_name": author_name,
                    "isbn": isbn,
                    "isbns_m": isbns,
                    "publish_date": publish_date,
                    "number_of_pages_median": number_of_pages_median,
                    "ratings_average": ratings_average,
                    "has_fulltext": has_fulltext,
                    "cover": cover,
                }
            )

        return num_found, results
