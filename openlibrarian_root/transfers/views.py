from django.shortcuts import render, redirect
from utils.Session import async_get_session_info, async_logged_in
from utils.Login import check_npub, check_npub_of_nsec
from utils.Connections import clone_follow
from circulation_desk.forms import npubForm

# Create your views here.
async def transfers(request):
    """Returns the user settings view."""
    # Return to index if the user profile is not logged in
    if await async_logged_in(request) == False:
        return redirect('circulation_desk:index')
    # Otherwise return the user profile
    else:
        session = await async_get_session_info(request)
        return render(request, 'transfers/transfers.html', session)
    
# Import social lists
async def social_clone(request):
    """View for the login (npub) page of the website."""
    # If not logged in then redirect to the home page
    if await async_logged_in(request)==False:
        return redirect('circulation_desk:index')
    else:
        session = await async_get_session_info(request)
        if not session["nsec"]:
            return render(request, 'transfers/social_clone.html', session)

    if request.method == 'GET':
        form = npubForm()
        context = {
            'form': form,
            'session': session
        }
        return render(request, 'transfers/social_clone.html', context)

    if request.method == 'POST':
        form = npubForm(request.POST)
        if not form.is_valid():
            context = {
                'form': form,
                'session': session
            }
            return render(request, 'transfers/social_clone.html', context)

        npub = request.POST.get('npub')

        valid_npub = check_npub(npub)
        npub_of_nsec = check_npub_of_nsec(npub=npub, nsec=session["nsec"])

        if valid_npub and not npub_of_nsec:
            await clone_follow(relays=session["relays"], npub=npub, nsec=session["nsec"])
            context = {
                'form': form,
                'session': session,
                'success_message': "Imported Friends and Foes!"
            }
            return render(request, 'transfers/social_clone.html', context)
        else:
            if not valid_npub:
                err_txt = "Invalid NPUB."
            else:
                err_txt = "Please provide an NPUB which is different from the one associated with your NSEC."
            context = {
                'form': form,
                'session': session,
                'error_message': err_txt
            }
            return render(request, 'transfers/profile_clone.html', context)
        

# Import profile
async def profile_clone(request):
    """View for the login (npub) page of the website."""
    # If not logged in then redirect to the home page
    if await async_logged_in(request)==False:
        return redirect('circulation_desk:index')
    else:
        session = await async_get_session_info(request)
        if not session["nsec"]:
            return render(request, 'transfers/profile_clone.html', session)

    if request.method == 'GET':
        form = npubForm()
        context = {
            'form': form,
            'session': session
        }
        return render(request, 'transfers/profile_clone.html', context)

    if request.method == 'POST':
        form = npubForm(request.POST)
        if not form.is_valid():
            context = {
                'form': form,
                'session': session
            }
            return render(request, 'transfers/profile_clone.html', context)

        npub = request.POST.get('npub')

        valid_npub = check_npub(npub)
        npub_of_nsec = check_npub_of_nsec(npub=npub, nsec=session["nsec"])

        if valid_npub and not npub_of_nsec:
            # TODO: Import profile function
            # TODO: Update session data with profile
            print("Importing Profile...")
            context = {
                'form': form,
                'session': session,
                'success_message': "Profile Imported!"
            }
            return render(request, 'transfers/profile_clone.html', context)
        else:
            if not valid_npub:
                err_txt = "Invalid NPUB."
            else:
                err_txt = "Please provide an NPUB which is different from the one associated with your NSEC."
            context = {
                'form': form,
                'session': session,
                'error_message': err_txt
            }
            return render(request, 'transfers/profile_clone.html', context)
