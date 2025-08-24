from django.shortcuts import render, redirect
from utils.Session import async_get_session_info, async_logged_in
from utils.Login import check_npub
from utils.Connections import clone_follow
from utils.Network import nostr_prepare, get_event_relays
from circulation_desk.forms import NpubForm


# Create your views here.
async def transfers(request):
    """Returns the user settings view."""
    # Return to index if the user profile is not logged in
    if not await async_logged_in(request):
        return redirect("circulation_desk:index")
    # Otherwise return the user profile
    else:
        session = await async_get_session_info(request)
        return render(request, "transfers/transfers.html", session)


# Import social lists
async def social_clone(request):
    """View for the login (npub) page of the website."""
    # If not logged in then redirect to the home page
    if not await async_logged_in(request):
        return redirect("circulation_desk:index")
    else:
        session = await async_get_session_info(request)
        noted = None
        events = None
        event_relay = None
        if not session["nsec"]:
            return render(request, "transfers/social_clone.html", session)

    if request.method == "GET":
        form = NpubForm()

    elif request.method == "POST":
        form = NpubForm(request.POST)
        if form.is_valid():
            copy_npub = request.POST.get("npub")
            valid_npub = check_npub(copy_npub)

            if valid_npub and copy_npub != session["npub"]:
                event_list = await clone_follow(
                    relays=session["relays"], npub=copy_npub
                )
                events = nostr_prepare(event_list)
                event_relay = get_event_relays(relays_dict=session["relays"])
            else:
                if not valid_npub:
                    noted = "false:Invalid NPUB."
                else:
                    noted = "false:Please provide an NPUB which is different from the one already in use."

    context = {
        "form": form,
        "session": session,
        "events": events,
        "event_relay": event_relay,
        "noted": noted,
    }
    return render(request, "transfers/social_clone.html", context)


# Import profile
async def profile_clone(request):
    """View for the login (npub) page of the website."""
    # If not logged in then redirect to the home page
    if not await async_logged_in(request):
        return redirect("circulation_desk:index")
    else:
        session = await async_get_session_info(request)
        if not session["nsec"]:
            return render(request, "transfers/profile_clone.html", session)

    if request.method == "GET":
        form = NpubForm()
        context = {"form": form, "session": session}
        return render(request, "transfers/profile_clone.html", context)

    if request.method == "POST":
        form = NpubForm(request.POST)
        if not form.is_valid():
            context = {"form": form, "session": session}
            return render(request, "transfers/profile_clone.html", context)

        copy_npub = request.POST.get("npub")

        valid_npub = check_npub(copy_npub)

        if valid_npub and copy_npub != session["npub"]:
            # TODO: Import profile function
            # TODO: Update session data with profile
            print("Importing Profile...")
            context = {
                "form": form,
                "session": session,
                "success_message": "Profile Imported!",
            }
            return render(request, "transfers/profile_clone.html", context)
        else:
            if not valid_npub:
                err_txt = "Invalid NPUB."
            else:
                err_txt = "Please provide an NPUB which is different from the one associated with your NSEC."
            context = {"form": form, "session": session, "error_message": err_txt}
            return render(request, "transfers/profile_clone.html", context)
