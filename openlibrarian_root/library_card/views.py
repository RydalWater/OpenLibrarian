from django.shortcuts import render
from django.http import JsonResponse
from utils.Session import async_logged_in, async_get_session_info, async_set_session_info
from utils.Profile import fetch_profile_info
from utils.Library import fetch_libraries, prepare_libraries
from utils.Interests import fetch_interests
from utils.Login import check_npub
from utils.Progress import fetch_progress
from utils.Review import fetch_reviews
from utils.Constants import INTERESTS_HASHMAP
import asyncio

async def fetch_user_data(npub: str, read_only: bool = False):
    """Fetch user data from relays"""
    profile, relays, added_relays = await fetch_profile_info(npub=npub)
    tasks = [fetch_libraries(npub=npub, relays=relays), fetch_interests(npub, relays)]
    raw_libraries, interest_list = await asyncio.gather(*tasks)
    libraries = await prepare_libraries(libEvents=raw_libraries, npub=npub, read_only=read_only)
    
    # Get list of ISBNs and then create progress object
    isbns = []
    for library in libraries:
        if library["s"] in ("CR", "HR"):
            for book in library["b"]:
                if "Hidden" not in book["i"]:
                    isbns.append(book["i"])
    tasks_prog_review = [fetch_progress(npub=npub, isbns=isbns, relays=relays), fetch_reviews(npub=npub, relays=relays, isbns=isbns)]
    progress, reviews = await asyncio.gather(*tasks_prog_review)

    return profile, relays, added_relays, libraries, interest_list, progress, reviews

def library_card(request, npub: str=None):
    """Returns view for Library."""
    return render(request, 'library_card/card.html')

async def card_data(request, npub: str=None):
    """Returns JSONResponse for Library card data."""
    if await async_logged_in(request):
        session = await async_get_session_info(request)
    else:
        session = None
    
    if session and npub == session['npub']:
        nym = session['nym']
        profile = session['profile']
        interest_list = session['interests']
        libraries = session['libraries']
        progress = session['progress']
        owner = True
    else:
        profile, relays, added_relays, libraries, interest_list, progress, reviews = await fetch_user_data(npub=npub, read_only=True)
        nym = profile['nym']
        owner = False

    displayname = profile['displayname']
    about = profile['about']
    picutre = profile['picture']
    interests = []
    for key, value in INTERESTS_HASHMAP.items():
        for interest in interest_list:
            if value == interest:
                interests.append(key)
                break
    if len(interests) == 0:
        interests.append("No interests set, they are an enigma!")

    current_books = {}
    to_read = 0
    read = 0
    current = 0
    for library in libraries:
        if library["s"] == "CR":
            for book in library["b"]:
                current += 1
                if book["h"] == "N":
                    current_books[f"{current}"] = {"t": book["t"], "a": book["a"], "i" : book["i"]}
                else:
                    current_books[f"{current}"] = {"t": "A Mysterious Book", "a": "Unknown Author", "i" : "hidden"}
        elif library["s"] in("TRS", "TRW"):
            for book in library["b"]:
                to_read += 1
        elif library["s"] == "HR":
            for book in library["b"]:
                read += 1
    
    if current_books == {}:
        current_books[f"{current}"] = {"t": "This user is currently between books."}

    context = {
        'nym': nym,
        'displayname': displayname,
        'about': about,
        'picture': picutre,
        'interests': interests,
        'current_books': current_books,
        'to_read': to_read,
        'read': read,
        'owner': owner,
        'progress': progress
    }
    return JsonResponse(context)

async def explore_profile(request, npub: str=None):
    """Log-in via npub and return JSONResponse."""
    
    # Then log-in via npub
    valid_npub = check_npub(npub)
    if valid_npub:
        # Fetch Profile Info and set Session Data
        profile, relays, added_relays, libraries, interests, progress, reviews = await fetch_user_data(npub=npub, read_only=True)
        nym = profile.get('nym')

        await async_set_session_info(request, npub=npub, nym=nym, relays=relays, def_relays=added_relays, profile=profile, interests=interests, libraries=libraries, progress=progress, reviews=reviews)

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})
