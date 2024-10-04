from django.shortcuts import render, redirect
from django.core.cache import cache
from django.contrib import messages
from utils.Session import async_logged_in, async_get_session_info, async_set_session_info, cache_get, cache_set, cache_key, cache_delete
from utils.Profile import edit_profile_info, edit_relay_list, fetch_profile_info
from utils.Login import check_nsec
from utils.Connections import fetch_social_list
from nostr_sdk import Keys

# Users Settings View
async def user_settings(request):
    """Returns the user settings view."""
    # Return to index if the user profile is not logged in
    if await async_logged_in(request) == False:
        return redirect('circulation_desk:index')
    # Otherwise return the user profile
    else:
        session = await async_get_session_info(request)
        return render(request, 'almanac/user_setting.html', session)


# User profile view
async def user_profile(request):
    """Returns the user profile view."""
    # Return to index if the user profile is not logged in
    if await async_logged_in(request) == False:
        return redirect('circulation_desk:index')

    # Otherwise return the user profile
    else:
        session = await async_get_session_info(request)

        if request.method == 'GET':
            return render(request, 'almanac/user_profile.html', session)

        # If POST then update the user profile
        elif request.method == 'POST' and await async_logged_in(request) and request.POST.get('save'):
            # Get Values from Screen
            nym_field = request.POST.get('edit_nym', None)
            nip05_field = request.POST.get('edit_nip05', None)
            displayname_field = request.POST.get('edit_displayname', None)
            about_field = request.POST.get('edit_about', None)
            picture_field = request.POST.get('edit_picture', None)

            # Update the profile
            nym_profile = {
                "nym" : nym_field,
                "nip05" : nip05_field,
                "displayname" : displayname_field,
                "about" : about_field,
                "picture" : picture_field
            }

            if check_nsec(session['nsec']):
                await edit_profile_info(nym_profile, session['relays'], session['nsec'])

            # Update Session data and re-extract
            profile = {
                "nym" : nym_field,
                "nip05" : nip05_field,
                "displayname" : displayname_field,
                "about" : about_field,
                "picture" : picture_field
            }

            await async_set_session_info(request, profile=profile, nym=nym_field)
            session = await async_get_session_info(request)

            return render(request, 'almanac/user_profile.html', session)
        
        # Perform refresh of the user profile content
        if request.method == 'POST' and await async_logged_in(request) and request.POST.get('refresh'):
            keys = Keys.parse(session['nsec'])
            if session['relays'] is None:
                profile, relays = await fetch_profile_info(npub=keys.public_key().to_bech32())
            else:
                profile, relays = await fetch_profile_info(npub=keys.public_key().to_bech32(), relays=session['relays'])
            npub = keys.public_key().to_bech32()
            nsec = keys.secret_key().to_bech32()
            nym = profile.get('nym')
            
            await async_set_session_info(request,npub=npub,nsec=nsec,nym=nym,relays=relays, profile=profile)
            session = await async_get_session_info(request)
            return render(request, 'almanac/user_profile.html', session)
        
        # TODO: Add functionality to handle profile uploads with Nostr.Build API


# User relays view
async def user_relays(request):
    """Returns the user relays view."""
    # Clear any any error messages
    messages.success(request, '')

    # Return to index if the user profile is not logged in
    if await async_logged_in(request) == False:
        return redirect('circulation_desk:index')

    # Otherwise return the user relays
    else:
        # get relay data from session and create a modified copy
        temp_session = await async_get_session_info(request)
        if temp_session['mod_relays'] is None or request.POST.get('cancel'):
            mod_relays = temp_session['relays']
            await async_set_session_info(request, mod_relays=mod_relays)
              
        # If GET then return the user relays
        if request.method == 'GET':
            session = await async_get_session_info(request)
            return render(request, 'almanac/user_relays.html', session)
        
        # If POST then update the user relays
        elif request.method == 'POST':
            session = await async_get_session_info(request)

            # Add_relay button modfies the content of the mod_real updates session information
            if request.POST.get('add_relay') and request.POST.get('add_relay_url') and request.POST.get('relay_option'):
                if request.POST.get('relay_option') == "R":
                    session["mod_relays"][request.POST.get('add_relay_url')] = "READ"
                elif request.POST.get('relay_option') == "W":
                    session["mod_relays"][request.POST.get('add_relay_url')] = "WRITE"
                elif request.POST.get('relay_option') == "B":
                    session["mod_relays"][request.POST.get('add_relay_url')] = None
                await async_set_session_info(request, mod_relays=session["mod_relays"])

            # Remove_relay button modfies the content of the mod_real updates session information
            elif request.POST.get('remove'):
                # Check if there is at least one read and one write relay before removing
                read_count = 0
                write_count = 0
                for relay in session["mod_relays"]:
                    if session["mod_relays"][relay] == "READ":
                        read_count += 1
                    elif session["mod_relays"][relay] == "WRITE":
                        write_count += 1
                    else:
                        read_count += 1
                        write_count += 1
                
                if read_count == 1 and session["mod_relays"][request.POST.get('remove')] in ("READ", None) or \
                write_count == 1 and session["mod_relays"][request.POST.get('remove')] in ("WRITE", None):
                    messages.error(request, "Cannot remove relay. You must have at least one read and one write.")
                else:            
                    del session["mod_relays"][request.POST.get('remove')]
                    await async_set_session_info(request, mod_relays=session["mod_relays"])

            # Save changes submits event to write relays.
            elif request.POST.get('save'):
                if check_nsec(session['nsec']):
                    await edit_relay_list(session['relays'], session["mod_relays"], session['nsec'])
                    await async_set_session_info(request, relays=session["mod_relays"])


        session = await async_get_session_info(request)
        return render(request, 'almanac/user_relays.html', session)
    
# User following view
async def user_friends(request):
    """Returns the user following view."""
    # Return to index if the user profile is not logged in
    if not await async_logged_in(request):
        return redirect('circulation_desk:index')
    else:
        session = await async_get_session_info(request)
        key_str = "user_connections"

        if request.method == 'GET':
            # Check if the friends list is cached
            connctions = await cache_get(await cache_key(key_str,session))
            
            if connctions is None:
                friends = await fetch_social_list(relays=session['relays'], npub=session['npub'], list_type="follow")
                muted = await fetch_social_list(relays=session['relays'], npub=session['npub'], list_type="mute")
                
                # Cache the friends list for 30 minutes
                await cache_set(await cache_key(key_str,session), {'friends': friends, 'muted': muted}, 1800)
            else:
                friends = connctions['friends']
                muted = connctions['muted']
            
        # POST requests
        if request.method == 'POST':
            if request.POST.get('refresh'):
                friends = await fetch_social_list(relays=session['relays'], npub=session['npub'], list_type="follow")
                muted = await fetch_social_list(relays=session['relays'], npub=session['npub'], list_type="mute")
                
                # Cache the friends list for 30 minutes
                await cache_delete(await cache_key(key_str,session))
                await cache_set(await cache_key(key_str,session), {'friends': friends, 'muted': muted}, 1800)

        return render(request, 'almanac/user_friends.html', {'session': session, 'friends': friends, 'muted': muted})