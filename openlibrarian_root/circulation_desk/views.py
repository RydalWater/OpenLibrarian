from django.shortcuts import render, redirect
from django.core.cache import cache
from nostr_sdk import Keys
from mnemonic import Mnemonic
from utils.Session import async_logged_in, async_get_session_info, async_set_session_info
from utils.Login import check_npub, check_nsec, check_mnemonic
from utils.Profile import fetch_profile_info, edit_relay_list
from utils.Library import fetch_libraries
from utils.Interests import fetch_interests
from circulation_desk.forms import SeedForm, npubForm, nsecForm
import asyncio

# Basic view for home page
async def index(request):
    """View for the Circulation Desk (homepage) of the website."""
    context = await async_get_session_info(request)
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
        form = npubForm()
        context = {
            'form': form
        }
        return render(request, 'circulation_desk/login_npub.html', context)

    if request.method == 'POST':
        form = npubForm(request.POST)
        if not form.is_valid():
            context = {
                'form': form
            }
            return render(request, 'circulation_desk/login_npub.html', context)

        npub = request.POST.get('npub')

        valid_npub = check_npub(npub)

        if valid_npub:
            # Fetch Profile Info and set Session Data
            profile, relays = await fetch_profile_info(npub=npub)
            tasks = [fetch_libraries(npub=npub, nsec=None, relays=relays), fetch_interests(npub, relays)]
            libraries, interests = await asyncio.gather(*tasks)
            nym = profile.get('nym')

            await async_set_session_info(request, npub=npub, nym=nym, relays=relays, profile=profile, interests=interests, libraries=libraries)
            return redirect('circulation_desk:index')
        else:
            context = {
                'form': form,
                'error_message': "Invalid NPUB"
            }
            return render(request, 'circulation_desk/login_npub.html', context)
        
async def login_nsec_view(request):
    """View for the login (nsec) page of the website."""
    # If already logged in then redirect to the home page
    if await async_logged_in(request):
        return redirect('circulation_desk:index')
    
    if request.method == 'GET':
        form = nsecForm()
        context = {
            'form': form
        }
        return render(request, 'circulation_desk/login_nsec.html', context)

    if request.method == 'POST':
        form = nsecForm(request.POST)
        if not form.is_valid():
            context = {
                'form': form
            }
            return render(request, 'circulation_desk/login_nsec.html', context)

        nsec = request.POST.get('nsec')
        valid_nsec = check_nsec(nsec)

        if valid_nsec:
            keys = Keys.parse(request.POST.get('nsec'))
            # Fetch Profile Info and set Session Data
            npub = keys.public_key().to_bech32()
            nsec = keys.secret_key().to_bech32()
            
            profile, relays = await fetch_profile_info(npub=npub)
            tasks = [fetch_libraries(npub=npub, nsec=nsec, relays=relays), fetch_interests(npub, relays)]
            libraries, interests = await asyncio.gather(*tasks)
            nym = profile.get('nym')

            await async_set_session_info(request,npub=npub,nsec=nsec,nym=nym,relays=relays, profile=profile, libraries=libraries, interests=interests)
            return redirect('circulation_desk:index')
        else:
            context = {
                'form': form,
                'error_message': "Invalid NSEC"
            }
            return render(request, 'circulation_desk/login_nsec.html', context)

async def login_seed_view(request):
    """View for the login (seed) page of the website."""
    # If already logged in then redirect to the home page
    if await async_logged_in(request):
        return redirect('circulation_desk:index')
    
    word_list = Mnemonic("english").wordlist

    if request.method == 'GET':
        form = SeedForm()
        context = {
            'form': form,
            'word_list': word_list
        }
        return render(request, 'circulation_desk/login_seed.html', context)

    if request.method == 'POST':
        form = SeedForm(request.POST)
        if not form.is_valid():
            context = {
                'form': form,
                'word_list': word_list
            }
            return render(request, 'circulation_desk/login_seed.html', context)

        mnemonic = ' '.join([form.cleaned_data[f'word{i}'] for i in range(1, 13)])
        valid_seed = check_mnemonic(mnemonic)

        if valid_seed:
            keys = Keys.from_mnemonic(mnemonic, "")
            # Fetch Profile Info and set Session Data
            npub = keys.public_key().to_bech32()
            nsec = keys.secret_key().to_bech32()
            profile, relays = await fetch_profile_info(npub=npub)
            tasks = [fetch_libraries(npub=npub, nsec=nsec, relays=relays), fetch_interests(npub, relays)]
            libraries, interests = await asyncio.gather(*tasks)
            nym = profile.get('nym')

            await async_set_session_info(request,npub=npub,nsec=nsec,nym=nym,relays=relays, profile=profile, libraries=libraries, interests=interests)
            return redirect('circulation_desk:index')
        else:
            context = {
                'form': form,
                'error_message': "Invalid Seed",
                'word_list': word_list
            }
            return render(request, 'circulation_desk/login_seed.html', context)

def logout_view(request):
    """View for the logout page of the website."""
    # Delete session data
    request.session.flush()

    # Clear cache
    cache.clear()
    return render(request, 'circulation_desk/logout.html') 

async def create_account_view(request):
    """View for the create account page of the website."""
    
    # If already logged in then redirect to the home page
    if await async_logged_in(request) and not any(key in request.POST for key in ['confirm_seed', 'generate_seed']):
        return redirect('circulation_desk:index')

    # Handle generating new keys/mnemonic 
    if request.method == 'POST' and 'generate_seed' in request.POST:
        mnemonic = Mnemonic("english")
        seed = mnemonic.generate(strength=128)
        words = seed.split(" ")
        keys = Keys.from_mnemonic(seed,"")
        nsec = keys.secret_key().to_bech32()
        npub = keys.public_key().to_bech32()

        # Set Session Data
        await async_set_session_info(request,npub=npub,nsec=nsec)

        context = {
            'words': words,
            'nsec': nsec,
            'npub': npub
        }
        return render(request, 'circulation_desk/create_account.html', context)
    
    # Handle confirming the new account
    if request.method == 'POST' and 'confirm_seed' in request.POST:
        return redirect('circulation_desk:create-account-confirm')
        
    if request.method == 'GET':
        return render(request, 'circulation_desk/create_account.html', context={})

async def create_account_confirm_view(request):
    """View for the create account confirm page of the website."""
    
    # If not already logged in then redirect to the home page
    if await async_logged_in(request) == False:
        return redirect('circulation_desk:index')
    
    # Default values for npub/confirmation
    session = await async_get_session_info(request)

    # Get full list of possible words
    word_list = Mnemonic("english").wordlist
    
    # If POST and all of the word fields have been completed attempt to 
    if request.method == 'POST':
        form = SeedForm(request.POST)
        if form.is_valid():
            mnemonic = ' '.join([form.cleaned_data[f'word{i}'] for i in range(1, 13)])
            if check_mnemonic(mnemonic):
                keys = Keys.from_mnemonic(mnemonic,"")
                if keys.public_key().to_bech32() == session['npub']:
                    private_key_confirmed = "Success"

                    # Set Session Data
                    nsec = keys.secret_key().to_bech32()
                    # Build default set of relays for user and set in session
                    session_relays = {}
                    mod_relays = {
                        "wss://relay.damus.io": None,
                        "wss://relay.primal.net": None,
                        "wss://nos.lol": None,
                        "wss://nostr.mom": None,
                    }
                    await edit_relay_list(session_relays, mod_relays, nsec)
                    
                    await async_set_session_info(request,nsec=nsec, relays=mod_relays)
                else:
                    private_key_confirmed = "Mnemonic does not match NPUB"
            else:
                private_key_confirmed = "Invalid mnemonic"

            context = {
                'form': form,
                'npub': session['npub'],
                'private_key_confirmed': private_key_confirmed,
                'word_list' : word_list

            }
            return render(request, 'circulation_desk/create_account_confirm.html', context)

    form = SeedForm()
    context = {
        'form': form,
        'npub': session['npub'],
        'private_key_confirmed' : None,
        'word_list' : word_list
    }
    return render(request, 'circulation_desk/create_account_confirm.html', context)