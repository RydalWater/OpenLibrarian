from django.shortcuts import render, redirect
from utils.Session import async_logged_in, async_get_session_info, async_set_session_info, cache_get, cache_set, cache_key, cache_delete
from utils.Profile import edit_profile_info, edit_relay_list, fetch_profile_info
from utils.Connections import fetch_social_list, add_follow, remove_follow
from utils.Network import nostr_prepare
import os, ast

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
        events = None
        noted = None
            
        # If POST then update the user profile
        if request.method == 'POST' and await async_logged_in(request) and request.POST.get('save'):
            # Get Values from Screen
            nym_field = request.POST.get('edit_nym', None)
            nip05_field = request.POST.get('edit_nip05', None)
            displayname_field = request.POST.get('edit_displayname', None)
            about_field = request.POST.get('edit_about', None)
            picture_field = request.POST.get('edit_picture', None)

            # Update the profile
            session["profile"]["nym"] = nym_field
            session["profile"]["nip05"] = nip05_field
            session["profile"]["displayname"] = displayname_field
            session["profile"]["about"] = about_field
            session["profile"]["picture"] = picture_field

            builder = await edit_profile_info(session["profile"])
            events = nostr_prepare([builder])

            # Update Session data and re-extract
            await async_set_session_info(request, profile=session["profile"], nym=nym_field)
            session = await async_get_session_info(request)
        
        # Perform refresh of the user profile content
        if request.method == 'POST' and await async_logged_in(request) and "refresh" in request.POST:
            npub = session['npub']
            if session['relays'] is None:
                profile, relays, added_relays = await fetch_profile_info(npub=npub)
            else:
                profile, relays, added_relays = await fetch_profile_info(npub=npub, relays=session['relays'])
            nym = profile.get('nym')
            
            await async_set_session_info(request,npub=npub,nym=nym,relays=relays, def_relays=added_relays, profile=profile)
            session = await async_get_session_info(request)
            noted = "true:Refreshed"

        context  = {
            "session": session,
            "noted": noted,
            "events": events
        }
        
        return render(request, 'almanac/user_profile.html', context=context)
        
        # TODO: Add functionality to handle profile uploads with Nostr.Build API


# User relays view
async def user_relays(request):
    """Returns the user relays view."""
    # Return to index if the user profile is not logged in
    if await async_logged_in(request) == False:
        return redirect('circulation_desk:index')

    # Otherwise return the user relays
    else:
        noted = None
        events = None

        # get default relays from environment variable
        default_relays = ast.literal_eval(os.getenv("DEFAULT_RELAYS"))

        # Fetch session and make a copy
        session = await async_get_session_info(request)

        # If cancel is used or mod_relays is None then set mod_relays to relays
        temp_session = session.copy()

        if temp_session['mod_relays'] in [None, {}] or "mod_relays" not in temp_session.keys() or request.POST.get('cancel'):
            temp_session["mod_relays"] = session["relays"].copy()
            session["mod_relays"] = session["relays"].copy()
            await async_set_session_info(request, mod_relays=session["mod_relays"])

        # If POST then update the user relays
        if request.method == 'POST':
            # Add_relay button modfies the content of the mod_realy updates session information
            if request.POST.get('add_relay') and request.POST.get('add_relay_url') and request.POST.get('relay_option'):
                if request.POST.get('relay_option') == "R":
                    temp_session["mod_relays"][request.POST.get('add_relay_url')] = "READ"
                elif request.POST.get('relay_option') == "W":
                    temp_session["mod_relays"][request.POST.get('add_relay_url')] = "WRITE"
                elif request.POST.get('relay_option') == "B":
                    temp_session["mod_relays"][request.POST.get('add_relay_url')] = None
                session["mod_relays"] = temp_session["mod_relays"].copy()
                await async_set_session_info(request, mod_relays=session["mod_relays"] )

            # Remove_relay button modfies the content of the mod_real updates session information
            elif request.POST.get('remove'):
                # Check if there is at least one read and one write relay before removing
                read_count = 0
                write_count = 0
                for relay in temp_session["mod_relays"]:
                    if temp_session["mod_relays"][relay] == "READ":
                        read_count += 1
                    elif temp_session["mod_relays"][relay] == "WRITE":
                        write_count += 1
                    else:
                        read_count += 1
                        write_count += 1
                
                if read_count == 1 and temp_session["mod_relays"][request.POST.get('remove')] in ("READ", None) or \
                write_count == 1 and temp_session["mod_relays"][request.POST.get('remove')] in ("WRITE", None):
                    noted = "false:Cannot remove relay. You must have at least one read and one write."
                else:
                    del temp_session["mod_relays"][request.POST.get('remove')]
                    session["mod_relays"] = temp_session["mod_relays"].copy()
                    await async_set_session_info(request, mod_relays=session["mod_relays"])
            

            # Save changes submits event to write relays.
            elif request.POST.get('save'):
                if session['nsec'] and session['nsec'].upper() == "Y":
                    update, builder = await edit_relay_list(session['relays'], temp_session["mod_relays"])
                    if update:
                        events = nostr_prepare([builder])
                    session["relays"] = temp_session["mod_relays"].copy()
                    await async_set_session_info(request, relays=session["relays"])

        context = {
            "session": session,
            "default_relays": default_relays,
            "noted": noted,
            "events": events

        }
        return render(request, 'almanac/user_relays.html', context=context)
    
# User following view
async def user_friends(request):
    """Returns the user following view."""
    # Return to index if the user profile is not logged in
    if not await async_logged_in(request):
        return redirect('circulation_desk:index')
    else:
        session = await async_get_session_info(request)
        key_str = "user_connections"
        noted = None
        events = None

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
        elif request.method == 'POST':
            # Attempt to add new follow
            if request.POST.get('follow_user'):
                noted, build = await add_follow(session['relays'], npub=session['npub'], follow_id=request.POST.get('follow_user'))
                if build is not None:
                    events = nostr_prepare([build])                    
            elif "follow" in request.POST:
                noted = "false:Please provide npub or nip05."
            elif "refresh" in request.POST:
                noted = "true:Refreshed."
            elif "remove" in request.POST:
                noted, build = await remove_follow(session['relays'], npub=session['npub'], follow_id=request.POST.get('remove'))
                if build is not None:
                    events = nostr_prepare([build])

            # Fetch lists again
            friends = await fetch_social_list(relays=session['relays'], npub=session['npub'], list_type="follow")
            muted = await fetch_social_list(relays=session['relays'], npub=session['npub'], list_type="mute")
            
            # Cache the friends list for 30 minutes
            await cache_delete(await cache_key(key_str,session))
            await cache_set(await cache_key(key_str,session), {'friends': friends, 'muted': muted}, 1800)

        context = {
            "session": session,
            "friends": friends,
            "muted": muted,
            "events": events,
            "noted": noted
        }

        return render(request, 'almanac/user_friends.html', context=context)