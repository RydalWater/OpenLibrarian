from django.shortcuts import render, redirect
from glossary.forms import SearchForm
from utils.Session import async_logged_in, async_get_session_info, async_set_session_info, cache_get, cache_set, cache_key, cache_delete
from utils.OpenLibrary import search_books
from utils.Book import Book
from utils.Library import Library
from utils.Interests import Interests, fetch_interests
from utils.Progress import Progress
from utils.Review import Review
from utils.Constants import INTERESTS_HASHMAP, INTERESTS
from utils.Network import nostr_prepare


async def glossary(request):
    """Returns Simple view for Search."""
    # Return to index if the user profile is not logged in
    if await async_logged_in(request) == False:
        return redirect('circulation_desk:index')

    # Otherwise return the user profile
    else:
        session = await async_get_session_info(request)
        return render(request, 'glossary/glossary.html', session)
    

async def search(request):
    """Returns Simple view for Search."""
    # Return to index if the user profile is not logged in
    if await async_logged_in(request) == False:
        return redirect('circulation_desk:index')

    # Otherwise return the user profile
    else:
        # Current session info
        session = await async_get_session_info(request)
        # Cache key
        key = await cache_key("results", session)
        # Form
        form = SearchForm(request.POST or None)
        # Events
        events = None
        # Context
        context = {
                'session': session,
                'form': form,
                'noted': None,
            }
        
        # Handle Get request
        if request.method == 'GET':
            return render(request, 'glossary/search.html', context)

        # If POST then update the user profile
        elif request.method == 'POST' and await async_logged_in(request):
            if request.POST.get('add_book') and request.POST.get('shelf') != "":
                
                # Add book to library if not already in library
                isbn = request.POST.get('version')
                default_pages = request.POST.get('default_pages')
                shelf = request.POST.get('shelf')
                if request.POST.get('hidden'):
                    hidden = "Y"
                else:
                    hidden = "N" 

                isbns = []
                for library in session['libraries']:
                    for book in library['b']:
                        isbns.append(book['i'])
                if isbn not in isbns:
                    for library in session['libraries']:
                        if library['s'] == shelf:
                            event_list = []
                            # Build Book
                            book = Book(isbn=isbn,hidden=hidden)
                            await book.get_book()
                            library['b'].append(book.detailed())
                            # Add book to shelf and publish
                            lib = Library(dict=library, npub=session["npub"])
                            lib.build_event(npub=session["npub"])
                            event_list.append(lib.bevent)
                            
                            # Add book to progress
                            if library["s"] in ["CR", "HR"]:
                                progress = await Progress().new(isbn=isbn, default_pages=default_pages)
                                if library["s"] == "CR":
                                    progress.start_book()
                                else:
                                    progress.start_book()
                                    progress.end_book()
                                progress.build_event()
                                review = await Review().new(isbn=isbn)
                                session["reviews"][isbn] = review.detailed()
                                session["progress"][isbn] = progress.detailed()
                                event_list.append(progress.bevent)

                            # Prepare rough signed events
                            events = nostr_prepare(event_list)

                            # Update session
                            await async_set_session_info(request, libraries=session['libraries'], progess=session["progress"], reviews=session["reviews"])
                            break
                    noted = None
                else:
                    noted = "false:Book already in library."
                    events = None

                # Fetch cached results
                cached_results = await cache_get(key)
                context['page'] = cached_results['page']
                context['pages'] = cached_results['pages']
                context['num_results'] = cached_results['num_results']
                context['results'] = cached_results['results']
                context['noted'] = noted
                context['events'] = events

            elif (form.is_valid() and request.POST.get('search')) or request.POST.get('next') or request.POST.get('prev') or request.POST.get('go'):
                # Form fields
                search_field = form.cleaned_data['search_field']
                search_type = form.cleaned_data['search_type']
                sort_type = form.cleaned_data['sort_type']
                
                # Set page number
                if request.POST.get('search'):
                    page = 1
                elif request.POST.get('next'):
                    page = int(request.POST.get('next')) + 1
                    # Take the ceiling of page / 5
                elif request.POST.get('prev'):
                    page = int(request.POST.get('prev')) - 1
                elif request.POST.get('go'):
                    try:
                        page = int(request.POST.get('go_page'))
                        if page < 1:
                            page = 1
                        elif page > int(request.POST.get('go')):
                            page = int(request.POST.get('go'))
                    except:
                        page  = 1
                
                # Search
                if search_type in ['isbn', 'author', 'title', 'general']:
                    num_results, results = await search_books(**{search_type: search_field}, sort=sort_type, page=page)
                    if num_results:
                        context["page"] = page
                        context["pages"] = int(num_results // 20) + (num_results % 20 >= 1)
                        context["num_results"] = num_results
                        context["results"] = results
                    else:
                        context["num_results"] = 0
                        context["results"] = []
                        context["pages"] = 1
                        context["page"] = 1
                        print("Error: Failed to search.")
                    
                    cached_results = {
                        "num_results": context["num_results"],
                        "results": context["results"],
                        "pages": context["pages"],
                        "page": context["page"]
                    }
                    await cache_set(key, cached_results, timeout=900)
                else:
                    print("Error: Invalid search type.")

            return render(request, 'glossary/search.html', context)

# Intersts view 
async def interests(request):
    """Returns Simple view for interests."""
    # Return to index if the user profile is not logged in
    if await async_logged_in(request) == False:
        return redirect('circulation_desk:index')

    # Otherwise return the user profile
    else:
        session = await async_get_session_info(request)
        noted = None
        # Check for interests and set/pull from session
        if "interests" not in session.keys() or (request.POST and "refresh" in request.POST):
            interests = await fetch_interests(session["npub"], session["relays"])
            await async_set_session_info(request, interests=interests)
            session = await async_get_session_info(request)
            noted = "true:Refreshed."
        if session["interests"] == None:
            session["interests"] = []
        
        events = None
            
        # Handle Post request
        if request.method == 'POST':
            # Handle save button
            if request.POST.get('save'):
                checklist = request.POST.getlist('interests')
                interests = []
                for interest in checklist:
                    interests.append(INTERESTS_HASHMAP[interest])
                if sorted(interests) != sorted(session["interests"]):
                    await async_set_session_info(request, interests=interests)
                    interests_obj = Interests(list=interests)
                    interests_obj.build_event(npub=session["npub"])
                    events = nostr_prepare([interests_obj.bevent])

        # Find if interests are in hashmap values and return key
        session = await async_get_session_info(request)
        selected = []
        for key, value in INTERESTS_HASHMAP.items():
            for interest in session["interests"]:
                if value == interest:
                    selected.append(key)
                    break

        context = {
                'interests': INTERESTS,
                'selected': selected,
                'session': session,
                'noted': noted,
                'events' : events
            }

        return render(request, 'glossary/interests.html', context)