from django.shortcuts import render, redirect
from utils.Session import async_logged_in, async_get_session_info, async_set_session_info, cache_get, cache_set, cache_key, cache_delete
from utils.Library import fetch_libraries, Library
from utils.Book import Book
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
            await async_set_session_info(request, libraries=libraries)
        else:
            libraries = session["libraries"]
        
        # Order libraries by "s" in the following order "CR" > "TRS" > "TRW" > "HR"
        sorted_keys = ["CR", "TRS", "TRW", "HR"]
        libraries.sort(key=lambda x: sorted_keys.index(x["s"]), reverse=False)

        if request.method == 'GET' or (request.method == 'POST' and "refresh" in request.POST):
            # TODO: Add additional book information (page, available on OL, progress, start/end date, rating etc.) 
            context = {
                "libraries": libraries,
                "session": session
            }
            return render(request, 'library/library_shelves.html', context)
        
        if request.method == 'POST':
            book_info = request.POST.get('book_info').split("-")
            shelf_id = book_info[0]
            book_id = book_info[1]
            status = request.POST.get('status')
            if request.POST.get('hidden'):
                hidden = "Y"
            else:
                hidden = "N"

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
            # Update privacy only, pubish updated library and update session
            elif request.POST.get('update_privacy'):
                print("\nUpdating privacy only")
                for library in libraries:
                    if library["i"] == shelf_id:
                        for book in library["b"]:
                            if book["i"] == book_id and book["h"] != hidden:
                                book["h"] = hidden
                                lib = Library(dict=library, npub=session["npub"], nsec=session["nsec"])
                                lib.build_event(npub=session["npub"], nsec=session["nsec"])
                                await lib.publish_event(nsec=session["nsec"], nym_relays=session["relays"])
                                await async_set_session_info(request, libraries=libraries)
                                print("\t- Privacy updated")
                                break
                            elif book["i"] == book_id and book["h"] == hidden:
                                print("\t- No change")
                                break                    
            # Update the shelves
            elif request.POST.get('update_library'):
                print("\nUpdating library")
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
                "session": session
            }
            return render(request, 'library/library_shelves.html', context)