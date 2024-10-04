# Various functions to allow for quick maintaince of Nostr Network connections
from nostr_sdk import Client, Metadata, Event, EventBuilder, EventSource, Keys, init_logger, LogLevel
from datetime import timedelta
import os, ast

os.environ
async def nostr_get(client: Client, filters: list, wait: int, connect: bool=True, disconnect: bool=True, relays_dict: dict=None, relays_list: list=None):
    """Get events from relays and return"""
    init_logger(LogLevel.INFO)

    # Get default relays if needed
    if not relays_dict and not relays_list:
        print("No relays provided loading default relays.")
        relays_list = ast.literal_eval(os.getenv("DEFAULT_RELAYS"))
        print(relays_list)

    # Add and Connect to relays
    if relays_dict is not None:
        for relay in relays_dict:
            if relays_dict[relay] in [None, "READ"]:
                    await client.add_relay(relay)
    else:
        for relay in relays_list:
            await client.add_relay(relay)
    
    if connect:
        await client.connect()

    # Get the events
    if wait:
        td = timedelta(seconds=wait)
    else:
        td = timedelta(seconds=10)
    
    events = await client.get_events_of(filters, source=EventSource.relays(td))

    # Disconnect
    if disconnect:
        await client.disconnect()

    # Return
    return events

async def nostr_post(client: Client, event: Event=None, eventbuilder: EventBuilder=None, connect: bool=True, disconnect: bool=True, relays_dict: dict=None, relays_list: list=None):
    """Post event to relays"""
    # Get test_mode flag
    test_mode = os.getenv("TEST_MODE")
    if test_mode == "Y":
        print("TESTMODE: Running in test mode, with dummy keys.")
        keys = Keys.parse(os.getenv("TEST_NSEC"))

    # Get default relays if needed
    if not relays_dict and not relays_list:
        print("No relays provided loading default relays.")
        relays_list = ast.literal_eval(os.getenv("DEFAULT_RELAYS"))
        print(relays_list)

    # Add and Connect to relays
    if relays_dict is not None:
        for relay in relays_dict:
            if relays_dict[relay] in [None, "WRITE"]:
                    await client.add_relay(relay)
    else:
        for relay in relays_list:
            await client.add_relay(relay)

    # Post events except when in test mode.
    if test_mode != "Y":
        init_logger(LogLevel.INFO)
        # Connect
        if connect:
            await client.connect()

        # Post the event
        if eventbuilder:
            await client.send_event_builder(eventbuilder)
        elif event:
            await client.send_event(event)

        # Disconnect
        if disconnect:
            await client.disconnect()
    else:
        print("TESTMODE: Event not posted.")
        if eventbuilder:
            print(f"TESTMODE: {eventbuilder.to_unsigned_event(keys.public_key()).as_json()}")
        elif event:
            print(f"TESTMODE: {event.as_json()}")
        print("")

async def nostr_post_profile(client: Client, profile_meta:Metadata, connect: bool=True, disconnect: bool=True, relays_dict: dict=None, relays_list: list=None):
    """Post profile event to relays"""
    # Get test_mode flag
    test_mode = os.getenv("TEST_MODE")
    if test_mode == "Y":
        print("TESTMODE: Running in test mode, with dummy keys.")

    # Get default relays if needed
    if not relays_dict and not relays_list:
        print("No relays provided loading default relays.")
        relays_list = ast.literal_eval(os.getenv("DEFAULT_RELAYS"))
        print(relays_list)

    # Add and Connect to relays
    if relays_dict is not None:
        for relay in relays_dict:
            if relays_dict[relay] in [None, "WRITE"]:
                    await client.add_relay(relay)
    else:
        for relay in relays_list:
            await client.add_relay(relay)

    # Post events except when in test mode.
    if test_mode != "Y":
        init_logger(LogLevel.INFO)
        # Connect
        if connect:
            await client.connect()

        # Post the event
        await client.set_metadata(profile_meta)

        # Disconnect
        if disconnect:
            await client.disconnect()
    else:
        print("TESTMODE: Event not posted.")
        print(f"TESTMODE: {profile_meta.as_json()}")
        print("")
    