from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.cache import cache
from nostr_sdk import Event
from mnemonic import Mnemonic
from utils.Session import async_logged_in, async_get_session_info, async_set_session_info
from utils.Login import check_npub
from utils.Profile import fetch_profile_info, edit_relay_list
from utils.Library import fetch_libraries, prepare_libraries
from utils.Interests import fetch_interests
from utils.Progress import fetch_progress
from utils.Review import fetch_reviews
from utils.Network import nostr_push, nostr_prepare
from circulation_desk.forms import SeedForm, NpubForm, NsecForm
import asyncio, os, ast, json

# Basic view for home page
async def index(request):
    """View for the Circulation Desk (homepage) of the website."""
    session = await async_get_session_info(request)
    context = {
        'session': session,
    }
    # TODO: Update index page content
    # TODO: Add basic social feed
    return render(request, 'circulation_desk/index.html', context)

# Login Pages
async def login_view(request):
    """View for the base login page of the website."""
    # If already logged in then redirect to the home page
    if await async_logged_in(request):
        return redirect('circulation_desk:index')
    # TODO: Add logic for handling the login using external service (Alby, nos2x, etc.)
    return render(request, 'circulation_desk/login.html')

async def login_npub_view(request):
    """View for the login (npub) page of the website."""
    # If already logged in then redirect to the home page
    if await async_logged_in(request):
        return redirect('circulation_desk:index')
    
    if request.method == 'GET':
        form = NpubForm()
        context = {
            'form': form
        }
        return render(request, 'circulation_desk/login_npub.html', context)

    if request.method == 'POST':
        form = NpubForm(request.POST)
        if not form.is_valid():
            context = {
                'form': form
            }
            return render(request, 'circulation_desk/login_npub.html', context)

        npub = request.POST.get('npub')

        valid_npub = check_npub(npub)

        if valid_npub:
            # Fetch Profile Info and set Session Data
            profile, relays, added_relays = await fetch_profile_info(npub=npub)
            tasks = [fetch_libraries(npub=npub, relays=relays), fetch_interests(npub, relays)]
            raw_libraries, interests = await asyncio.gather(*tasks)
            libraries = await prepare_libraries(libEvents=raw_libraries, npub=npub, read_only=True)
            nym = profile.get('nym')

            # Get list of ISBNs and then create progress object
            isbns = []
            for library in libraries:
                if library["s"] in ("CR", "HR"):
                    for book in library["b"]:
                        if "Hidden" not in book["i"]:
                            isbns.append(book["i"])
            tasks_prog_review = [fetch_progress(npub=npub, isbns=isbns, relays=relays), fetch_reviews(npub=npub, relays=relays, isbns=isbns)]
            progress, reviews = await asyncio.gather(*tasks_prog_review)
 
            await async_set_session_info(request, npub=npub, nym=nym, relays=relays, def_relays=added_relays, profile=profile, interests=interests, libraries=libraries, progress=progress, reviews=reviews)
            return redirect('circulation_desk:index')
        else:
            context = {
                'form': form,
                'noted': "false:Invalid NPUB."
            }
            return render(request, 'circulation_desk/login_npub.html', context)

async def login_rw_view(request, form_class, template_name, redirect_url_on_error):
    """View for the login page of the website."""
    # If already logged in then redirect to the home page
    if await async_logged_in(request):
        return redirect('circulation_desk:index')

    if request.method == 'GET':
        form = form_class()
        context = {
            'form': form
        }
        if form_class == SeedForm:
            word_list = Mnemonic("english").wordlist
            context['word_list'] = word_list
        return render(request, template_name, context)

    if request.method == 'POST':

        # Get the frontend data including npub and decrypted events
        data = json.loads(request.body)
        npub = data.get('npubValue', '')
        hasNsec = data.get('hasNsec', '')
        decryptedEvents = data.get('decryptedEvents', '')

        # Get session data for access to the relays
        session = await async_get_session_info(request)

        if hasNsec == "Y":
            libraries = await prepare_libraries(libEvents=decryptedEvents, npub=npub)
            # Get list of ISBNs and then create progress object
            isbns = []
            for library in libraries:
                if library["s"] in ("CR", "HR"):
                    for book in library["b"]:
                        if "Hidden" not in book["i"]:
                            isbns.append(book["i"])
            tasks_prog_review = [fetch_progress(npub=npub, isbns=isbns, relays=session['relays']), fetch_reviews(npub=npub, relays=session['relays'], isbns=isbns)]
            progress, reviews = await asyncio.gather(*tasks_prog_review)
            await async_set_session_info(request,npub=npub,libraries=libraries, progress=progress, reviews=reviews)
            return JsonResponse({'redirect': '/'})
        else:
            return JsonResponse({'redirect': redirect_url_on_error, 'error_message': "Invalid Credentials"})

async def login_nsec_view(request):
    return await login_rw_view(request, NsecForm, 'circulation_desk/login_nsec.html', '/login/nsec')

async def login_seed_view(request):
    return await login_rw_view(request, SeedForm, 'circulation_desk/login_seed.html', '/login/seed')

async def login_nip07_view(request):
    # If already logged in then redirect to the home page
    if await async_logged_in(request):
        return redirect('circulation_desk:index')
    if request.method == 'GET':
        return render(request, 'circulation_desk/login_nip07.html')
    else:
        return await login_rw_view(request, None, 'circulation_desk/login_nip07.html', '/login/nip07')

@csrf_exempt
def logout_view(request):
    """View for the logout page of the website."""
    # Delete session data
    request.session.flush()
    # Clear cache
    cache.clear()

    if request.method == 'POST':
        return redirect('circulation_desk:index')
    return render(request, 'circulation_desk/logout.html') 

async def create_account_view(request):
    """View for the create account page of the website."""
    
    # If already logged in then redirect to the home page
    if await async_logged_in(request):
        return redirect('circulation_desk:index')
        
    context={"num_words":[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]}
    return render(request, 'circulation_desk/create_account.html', context=context)

async def create_account_confirm_view(request):
    """View for the create account confirm page of the website."""
     # If not already logged in then redirect to the home page
    if await async_logged_in(request) == True:
        return redirect('circulation_desk:index')
    
    form = SeedForm()
    word_list = Mnemonic("english").wordlist
    context = {
        'form': form,
        'word_list' : word_list
    }
    return render(request, 'circulation_desk/create_account_confirm.html', context)

@csrf_exempt
async def create_account_empty(request):
    """View for the create account empty account."""
    if not request.method == 'POST':
        return redirect('circulation_desk:index')
    
    # Get frontend data
    try:
        data = json.loads(request.body)
        npub = data.get('npubValue', '')
        nsec = data.get('hasNsec', '')
    except Exception as e:
        return JsonResponse({'result': 'Failed to create account'})
    
    
    # Build default set of relays for user
    session_relays = {}

    # Set default session relays
    default_relays = ast.literal_eval(os.getenv("DEFAULT_RELAYS"))
    mod_relays = {}
    for relay in default_relays:
        mod_relays[relay] = None


    update, builder = await edit_relay_list(session_relays, mod_relays)

    # Publish event
    events = nostr_prepare([builder])

    # Get default libraries and interests
    libraries = await prepare_libraries(libEvents=[], npub=npub)

    # Get default interests
    interests = await fetch_interests(npub, mod_relays)
    # Set Default Progress
    progress = {}
    reviews = {}

    # Set Session Data
    await async_set_session_info(request,libraries=libraries, interests=interests, relays=mod_relays, npub=npub, nsec=nsec, progress=progress, reviews=reviews)

    return JsonResponse({'raw_events': events})


@csrf_exempt
async def event_publisher(request):
    if not request.method == 'POST':
        return redirect('circulation_desk:index')
    
    # Get Session Info
    session = await async_get_session_info(request)
    message = None

    if session['nsec'] != None:
        # Get the Event from the request
        try:
            data = json.loads(request.body)
            events_json = data.get('events_json', '')
            # Convert events back from a json string
            events = json.loads(events_json)
        except Exception as e:
            return JsonResponse({'event_message': 'Unable to parse event.'})
        
        # Parse event and check it is valid
        post = []
        for se in events:
            try:
                event = Event.from_json(se)
            except Exception as e:
                event = None
                message = "Unable to parse event."

            if event:
                if not event.verify():
                    message = "Invalid event."
                else:
                    post.append(event)

        # Push events to relays
        if post:
            # Push events to relays
            try:
                await nostr_push(events=post, relays_dict=session['relays'])
                message = "Success: Updated."
            except Exception as e:
                message = "Unable to push event to relays."
        elif not message:
            message = "No events to push."

        # Response
        response = {'event_message': f'{message}'}
        return JsonResponse(response)
    else:
        return JsonResponse({'event_message': None})


# Login json response
@csrf_exempt
async def fetch_events(request):
    if not request.method == 'POST':
        return redirect('circulation_desk:index')
    
    # Get frontend data
    try:
        data = json.loads(request.body)
        npub = data.get('npubValue', '')
        nsec = data.get('hasNsec', '')
        refresh = data.get('refresh', '')
    except Exception as e:
        return JsonResponse({'raw_events': []})
    
    if refresh == "":
        profile, relays, added_relays = await fetch_profile_info(npub=npub)
        tasks = [fetch_libraries(npub=npub, relays=relays), fetch_interests(npub, relays)]
        raw_libraries, interests = await asyncio.gather(*tasks)
        nym = profile.get('nym', None)
        response = {'raw_events': raw_libraries}
        await async_set_session_info(request, nsec=nsec, nym=nym, relays=relays, def_relays=added_relays, profile=profile, interests=interests)

    else:
        if refresh == "shelves":
            relays = request.session.get('relays', None)
            libraries = await fetch_libraries(npub=npub, relays=relays)
            response = {'raw_events': libraries}
        else:
            response = {'raw_events': []}
    return JsonResponse(response)