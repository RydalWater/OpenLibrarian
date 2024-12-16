from django.shortcuts import render, redirect
from utils.Session import async_logged_in, async_get_session_info, async_set_session_info, cache_get, cache_set, cache_key, cache_delete
from utils.Library import fetch_libraries, Library
from utils.Progress import fetch_progress, Progress
from utils.Notifications import send_notification

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
        if "libraries" not in session.keys() or (request.POST and "refresh" in request.POST):
            libraries = await fetch_libraries(npub=session["npub"], nsec=session["nsec"], relays=session["relays"])
            # Get list of ISBNs and then create progress object
            isbns = []
            for library in libraries:
                if library["s"] in ("CR", "HR"):
                    for book in library["b"]:
                        if "Hidden" not in book["i"]:
                            isbns.append(book["i"])
                            
            progress = await fetch_progress(npub=session["npub"], isbns=isbns, relays=session["relays"])
            
            await async_set_session_info(request, libraries=libraries, progress=progress)
        else:
            libraries = session["libraries"]
        
        # Order libraries by "s" in the following order "CR" > "TRS" > "TRW" > "HR"
        sorted_keys = ["CR", "TRS", "TRW", "HR"]
        libraries.sort(key=lambda x: sorted_keys.index(x["s"]), reverse=False)

        if request.method == 'GET' or (request.method == 'POST' and "refresh" in request.POST):
            # TODO: Add additional book information (page, available on OL, progress, start/end date, rating etc.) 
            context = {
                "libraries": libraries,
                "session": session,
            }
            return render(request, 'library/library_shelves.html', context)
        
        if request.method == 'POST':
            # Get post data
            book_info = request.POST.get('book_info').split("-")
            shelf_id = book_info[0]
            book_id = book_info[1]
            status = request.POST.get('status')
            if request.POST.get('hidden'):
                hidden = "Y"
            else:
                hidden = "N"
            print(request.POST)
            stDt = request.POST.get('stDt', None)
            enDt = request.POST.get('enDt', None)
            unitRadio = request.POST.get('unitRadio', None)
            if unitRadio == "pages":
                max = request.POST.get('maxPage')
                cur = request.POST.get('currentPage')
            elif unitRadio == "pct":
                max = request.POST.get('maxPct')
                cur = request.POST.get('currentPct')
            else:
                max = None
                cur = None
                        
            # Remove book from library
            if request.POST.get('remove_book'):
                print("\nRemoving book")
                for library in libraries:
                    if library["i"] == shelf_id:
                        for book in library["b"]:
                            if book["i"] == book_id:
                                lib = Library(dict=library, npub=session["npub"], nsec=session["nsec"])
                                await lib.remove_book(isbn=book_id)
                                lib.build_event(npub=session["npub"], nsec=session["nsec"])
                                await lib.publish_event(nsec=session["nsec"], nym_relays=session["relays"])
                                await async_set_session_info(request, libraries=libraries)
                                print("\t- Book removed")
                                break

            # Update book information (inc hidden) and pubish updated library and update session
            elif request.POST.get('update'):
                print("\nUpdating book")
                for library in libraries:
                    if library["i"] == shelf_id:
                        for book in library["b"]:
                            if book["i"] == book_id:
                                # Handle changes to hidden
                                if  book["h"] != hidden:
                                    book["h"] = hidden
                                    lib = Library(dict=library, npub=session["npub"], nsec=session["nsec"])
                                    lib.build_event(npub=session["npub"], nsec=session["nsec"])
                                    await lib.publish_event(nsec=session["nsec"], nym_relays=session["relays"])
                                    await async_set_session_info(request, libraries=libraries)
                                    print("\t- Hidden updated")
                                elif book["h"] == hidden:
                                    print("\t- No change in Hidden")
                                
                                # Currently reading
                                if library["s"] in ["CR","HR"]:
                                    for each in session["progress"]:
                                        for k in each.keys():
                                            if k == book_id:
                                                progress_obj = Progress().parse_dict(each)
                                                progress_orig = progress_obj.detailed()
                                                session["progress"].remove(each)
                                                break
                                    
                                    # Handle date changes
                                    if progress_obj.started != stDt and stDt not in ("", None, "NA"):
                                        # TODO: Add notification for incorrect dates
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
                                        await progress_obj.publish_event(nsec=session["nsec"], nym_relays=session["relays"])

                                    # Update Session
                                    session["progress"].append(progress_obj.detailed())
                                    progress=session["progress"]
                                    await async_set_session_info(request, progress=progress)

                                    
            # Update the shelves
            elif request.POST.get('moved'):
                print("\nUpdating shelves")
                inlib = None
                outlib = None
                for library in libraries:
                    if library["i"] == shelf_id:
                        for book in library["b"]:
                            if book["i"] == book_id:
                                book_moving = book
                                outlib = Library(dict=library, npub=session["npub"], nsec=session["nsec"])
                                print(f"Removing book from library: {outlib.description}")
                                await outlib.remove_book(isbn=book_id)
                                libraries[libraries.index(library)] = outlib.__dict__()
                                break
                for library in libraries:
                    if library["s"] == status or (library["s"] == "HR" and status != "" and float(status)>=0):
                        inlib = Library(dict=library, npub=session["npub"], nsec=session["nsec"])
                        print(f"Adding book to library: {inlib.description}")
                        await inlib.add_book(dict=book_moving, hidden=hidden)
                        libraries[libraries.index(library)] = inlib.__dict__()
                        if library["s"] == "HR":
                            await send_notification(book=book_moving, nsec=session["nsec"], nym_relays=session["relays"], note_type="en", score=status)
                            # TODO: Add a review
                            print("\t- Add a review")
                        elif library["s"] == "CR":
                            await send_notification(book=book_moving, nsec=session["nsec"], nym_relays=session["relays"], note_type="st")
                        break
                
                if inlib and outlib:
                    # Update session data
                    await async_set_session_info(request, libraries=libraries)
                    # TODO: Publish Events in a more efficient way
                    inlib.build_event(npub=session["npub"], nsec=session["nsec"])
                    await inlib.publish_event(nsec=session["nsec"], nym_relays=session["relays"])
                    outlib.build_event(npub=session["npub"], nsec=session["nsec"])
                    await outlib.publish_event(nsec=session["nsec"], nym_relays=session["relays"])
                else:
                    # TODO: Add error message
                    print("Something went wrong")

            context = {
                "libraries": libraries,
                "session": session,
                # "progress": progress
            }
            return render(request, 'library/library_shelves.html', context)