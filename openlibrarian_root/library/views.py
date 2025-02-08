from django.shortcuts import render, redirect
from utils.Session import async_logged_in, async_get_session_info, async_set_session_info
from utils.Library import prepare_libraries, Library
from utils.Progress import fetch_progress, Progress
from utils.Notifications import build_notification
from utils.Review import fetch_reviews, Review
from utils.Network import nostr_prepare
import datetime, json, asyncio

async def library(request):
    """Returns Simple view for Library."""
    # Return to index if the user profile is not logged in
    if await async_logged_in(request) == False:
        return redirect('circulation_desk:index')
    else:
        session = await async_get_session_info(request)
        return render(request, 'library/library.html', session)
    
async def library_shelves(request):
    """Returns Simple view for Library."""
    # Return to index if the user is not logged in
    if await async_logged_in(request) == False:
        return redirect('circulation_desk:index')

    # Otherwise return the libary shelves
    else:
        session = await async_get_session_info(request)
        noted = None

        # Get data for post request when refreshing
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
            except:
                data = {}

        if "libraries" not in session.keys() or session["libraries"] is None or (request.method == 'POST' and data.get('refresh', None) is not None):
            if request.method == 'POST' and data.get('refresh', None) is not None:
                data = json.loads(request.body)
                npub = data.get('npubValue', '')
                decryptedEvents = data.get('decryptedEvents', '')
            else:
                npub = session["npub"]
                decryptedEvents = ''

            libraries = await prepare_libraries(libEvents=decryptedEvents, npub=npub)
            # Get list of ISBNs and then create progress object
            isbns = []
            for library in libraries:
                if library["s"] in ("CR", "HR"):
                    for book in library["b"]:
                        if "Hidden" not in book["i"]:
                            isbns.append(book["i"])
            tasks_prog_review = [fetch_progress(npub=npub, isbns=isbns, relays=session["relays"]), fetch_reviews(npub=npub, relays=session["relays"], isbns=isbns)]
            progress, reviews = await asyncio.gather(*tasks_prog_review)
            await async_set_session_info(request,npub=npub,libraries=libraries, progress=progress, reviews=reviews)
        else:
            libraries = session["libraries"]
            progress = session["progress"]
            reviews = session["reviews"]
        
        # Order libraries by "s" in the following order "CR" > "TRS" > "TRW" > "HR"
        sorted_keys = ["CR", "TRS", "TRW", "HR"]
        libraries.sort(key=lambda x: sorted_keys.index(x["s"]), reverse=False)

        if request.method == 'GET' or (request.method == 'POST' and data.get('refresh', None) is not None):
            # TODO: Add additional book information (page, available on OL, progress, start/end date, rating etc.) 
            context = {
                "libraries": libraries,
                "session": session,
                "progress": progress,
                "reviews": reviews,
                "noted": noted
            }
            return render(request, 'library/library_shelves.html', context)
        
        if request.method == 'POST':
            # Get general post data
            book_info = request.POST.get('book_info').split("-")
            shelf_id = book_info[0]
            book_id = book_info[1]
            status = request.POST.get('status', None)
            is_hidden = request.POST.get('hidden', None)
            stDt = request.POST.get('stDt', None)
            enDt = request.POST.get('enDt', None)
            unitRadio = request.POST.get('unitRadio', None)
            rating = request.POST.get('rating', None)

            # Get post type
            if request.POST.get('remove_book'):
                post_type = "remove"
            elif request.POST.get('update'):
                post_type = "update"
            elif request.POST.get('moved'):
                post_type = "moved"
            elif request.POST.get('finished'):
                post_type = "finished"

            # Set hidden
            if is_hidden:
                hidden = "Y"
            else:
                hidden = "N"
            
            # Set progress data
            if unitRadio == "pages":
                max = request.POST.get('maxPage')
                cur = request.POST.get('currentPage')
            elif unitRadio == "pct":
                max = request.POST.get('maxPct')
                cur = request.POST.get('currentPct')
            else:
                max = None
                cur = None

            # Validate progress data
            if stDt not in (None, "", "NA") and enDt not in (None, "", "NA"):
                if datetime.datetime.strptime(enDt, "%Y-%m-%d") < datetime.datetime.strptime(stDt, "%Y-%m-%d"):
                    noted = "false:End date is before start date."
            if enDt not in (None, "", "NA") and stDt in (None, "", "NA"):
                noted = "false:Start date is required when adding end date."
            if max not in (None, "") and cur not in (None, ""):
                if int(max) < int(cur):
                    noted = "false:Current progress is greater than max."
            
            event_list = []
            if noted is None:
                # Remove book from library
                if post_type == "remove":
                    for library in libraries:
                        if library["i"] == shelf_id:
                            for book in library["b"]:
                                if book["i"] == book_id:
                                    lib = Library(dict=library, npub=session["npub"])
                                    await lib.remove_book(isbn=book_id)
                                    lib.build_event(npub=session["npub"])
                                    event_list.append(lib.bevent)
                                    await async_set_session_info(request, libraries=libraries)
                                    break

                # Update book information (inc hidden) and pubish updated library and update session
                elif post_type == "update":
                    for library in libraries:
                        if library["i"] == shelf_id:
                            for book in library["b"]:
                                if book["i"] == book_id:
                                    # Handle changes to hidden
                                    if  book["h"] != hidden:
                                        book["h"] = hidden
                                        lib = Library(dict=library, npub=session["npub"])
                                        lib.build_event(npub=session["npub"])
                                        event_list.append(lib.bevent)
                                        await async_set_session_info(request, libraries=libraries)
                                    
                                    # Currently reading
                                    if library["s"] in ["CR","HR"]:
                                        
                                        progress_obj = Progress().parse_dict({book_id:progress[book_id]})
                                        progress_orig = progress_obj.detailed()
                                        del progress[book_id]
                                        
                                        # Handle date changes
                                        if progress_obj.started != stDt and stDt not in ("", None, "NA"):
                                            # TODO: Add notification for incorrect dates
                                            if enDt not in ("", None, "NA"):
                                                progress_obj.started = stDt
                                            else:
                                                progress_obj.start_book(started=stDt)

                                        if library["s"] == "HR":
                                            if progress_obj.ended != enDt and enDt not in ("", None, "NA"):
                                                # TODO: Add notification for incorrect dates
                                                progress_obj.end_book(ended=enDt)
                                        
                                        # Handle progress changes
                                        else:
                                            try:
                                                progress_obj.update_progress(unit=unitRadio, current=cur, max=max)
                                            except:
                                                print("\t- Error updating progress")                                  
                                        
                                        # Check if any changes and publish
                                        if progress_obj.detailed() != progress_orig:
                                            progress_obj.build_event()
                                            event_list.append(progress_obj.bevent)

                                        # Update Session
                                        progress[book_id] = progress_obj.detailed()
                                        await async_set_session_info(request, progress=progress)

                                        
                # Update the shelves
                elif post_type in ("moved", "finished"):
                    inlib = None
                    outlib = None
                    if post_type == "finished" and rating:
                        rating = int(rating)/2

                    for library in libraries:
                        if library["i"] == shelf_id:
                            for book in library["b"]:
                                if book["i"] == book_id:
                                    book_moving = book
                                    outlib = Library(dict=library, npub=session["npub"])
                                    await outlib.remove_book(isbn=book_id)
                                    libraries[libraries.index(library)] = outlib.__dict__()
                                    from_shelf = outlib.section
                                    break

                    for library in libraries:
                        if library["s"] == status or (library["s"] == "HR" and rating>=0.0):
                            inlib = Library(dict=library, npub=session["npub"])
                            await inlib.add_book(dict=book_moving, hidden=hidden)
                            libraries[libraries.index(library)] = inlib.__dict__()

                            # Update library (moving book to have read shelf)
                            if library["s"] == "HR":

                                # Update progress
                                if from_shelf != "CR":
                                    progress_obj = await Progress().new(isbn=book_moving["i"])
                                else:
                                    progress_obj = Progress().parse_dict({book_id:progress[book_id]})
                                    del progress[book_id]
                                if progress_obj.started in ("", None, "NA"):
                                    progress_obj.start_book()
                                progress_obj.end_book()
                                progress_obj.build_event()
                                event_list.append(progress_obj.bevent)
                                progress[book_id] = progress_obj.detailed()
                                
                                # Send notification (if moving from current reading shelve)
                                if from_shelf == "CR":
                                    try:
                                        float(rating)
                                        notify = await build_notification(book=book_moving, nym_relays=session["relays"], note_type="en", score=rating)
                                        review = await Review().review(isbn=book_moving["i"], rating=rating)
                                        event_list.append(notify)
                                        event_list.append(review.build_event().bevent)
                                        reviews[book_id] = review.detailed()
                                    except:
                                        pass
                                # Add progress and review to session
                                await async_set_session_info(request, progress=progress, reviews=reviews)
                            
                            # Update library (moving book to current reading shelf)
                            elif library["s"] == "CR":
                                # Update progress
                                if book_moving["i"] in [key for key in progress.keys()]:
                                    progress_obj = Progress().parse_dict({book_id:progress[book_id]})
                                    progress_obj.start_book()
                                    del progress[book_id]
                                else:
                                    progress_obj = await Progress().new(isbn=book_moving["i"])
                                    progress_obj.start_book()
                                
                                progress_obj.build_event()
                                event_list.append(progress_obj.bevent)
                                progress[book_id] = progress_obj.detailed()
                                await async_set_session_info(request, progress=progress)                           

                                # Send notification
                                notify = await build_notification(book=book_moving, nym_relays=session["relays"], note_type="st")
                                event_list.append(notify)
                            break
                    
                    if inlib and outlib:
                        # Update session data
                        await async_set_session_info(request, libraries=libraries)
                        # TODO: Publish Events in a more efficient way
                        inlib.build_event(npub=session["npub"])
                        event_list.append(inlib.bevent)
                        outlib.build_event(npub=session["npub"])
                        event_list.append(outlib.bevent)
                    else:
                        # TODO: Add error message
                        print("Something went wrong")
            
            # Prepare events for passing to signer
            if event_list != []:
                events = nostr_prepare(event_list)
            else:
                events = None

            context = {
                "libraries": libraries,
                "session": session,
                "progress": progress,
                "reviews": reviews,
                "noted": noted,
                "events": events
            }
            return render(request, 'library/library_shelves.html', context)
