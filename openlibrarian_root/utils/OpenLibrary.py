import aiohttp, asyncio
from utils.Book import get_cover

api_url = "https://openlibrary.org/search.json"

headers = {
    "User-Agent": "Unknown Application (no name yet, watch this space!!) - mynima@protonmail.com",
}

async def search_books(**kwargs):
    """Search for Books using Open Library API"""
    param_tags = {
        "author" : "author",
        "sort" : "sort",
        "title": "title",
        "isbn": "isbn",
        "general" : "q",
        "page" : "page",
        "lang" : "lang",
    }

    params = {}
    for key, value in kwargs.items():
        if key in param_tags:
            params[param_tags[key]] = value

    # Add fields parameter (default is title,author_name,isbn,publish_date,number_of_pages_median,ratings_average,has_fulltext) and limit (default is 10)
    if "fields" not in params:
        params["fields"]="title,author_name,isbn,publish_date,number_of_pages_median,ratings_average,has_fulltext"
    if "limit" not in params:
        params["limit"] = 20

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, headers=headers, params=params, timeout=10) as response:
            # If there is an error
            if response.status != 200:
                print(f"Error: {response.status}")
                return None, None

            # Convert response to JSON
            response_json = await response.json()

            # If there are no results
            if response_json["numFound"] == 0:
                print("No books found.")
                return 0, None
            
            # If there are results
            else:
                num_results = response_json["numFound"]
                docs = response_json["docs"]
                
                # Filter documents with necessary keys
                valid_docs = [
                    doc for doc in docs 
                    if "author_name" in doc and "isbn" in doc
                ]
                
                # List of tasks to gather covers concurrently
                cover_tasks = [
                    get_cover(session, doc["isbn"][0], "S") for doc in valid_docs
                ]
                
                # Gather all cover tasks concurrently
                covers = await asyncio.gather(*cover_tasks)
                
                # Construct results with gathered cover data
                results = []
                for doc, cover in zip(valid_docs, covers):
                    title = doc["title"]
                    author_name = ", ".join(doc["author_name"])
                    isbn = doc["isbn"][0]
                    publish_date = doc.get("publish_date", [None])[0]
                    has_fulltext = doc["has_fulltext"]
                    number_of_pages_median = doc.get("number_of_pages_median")
                    ratings_average = doc.get("ratings_average")
                
                    results.append(
                        {
                            "title": title,
                            "author_name": author_name,
                            "isbn": isbn,
                            "publish_date": publish_date,
                            "number_of_pages_median": number_of_pages_median,
                            "ratings_average": ratings_average,
                            "has_fulltext": has_fulltext,
                            "cover": cover,
                        }
                    )
                
                return num_results, results
