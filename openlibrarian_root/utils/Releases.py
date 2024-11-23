import aiohttp, markdown, os

async def fetch_releases():
        try:
             AUTH_TOKEN = os.getenv('AUTH_TOKEN')
        except:
            AUTH_TOKEN = None
        url = "https://api.github.com/repos/RydalWater/OpenLibrarian/releases"

        if AUTH_TOKEN is None:
            headers = {
                "Accept": "application/vnd.github.v3+json"
            }
        else:
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "Authorization" : f"Token {AUTH_TOKEN}"
            }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                releases = await response.json()
                return releases

async def get_release_info():
    releases = await fetch_releases()
    release_info = {}

    for release in releases:
        version = release['tag_name']
        release_date = release['published_at'].replace('T', ' ').replace('Z', ' UTC')
        release_notes = markdown.markdown(release["body"])
        if release_notes == "":
                release_notes = '<p> No Release Notes Provided. </p>'
        release_info[version] = {
            "release_date": release_date,
            "release_notes": release_notes
        }

    return release_info
