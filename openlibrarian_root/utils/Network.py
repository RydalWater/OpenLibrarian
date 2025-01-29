# Various functions to allow for quick maintaince of Nostr Network connections
from nostr_sdk import Client, Event, EventBuilder, EventSource, Keys, init_logger, LogLevel
from datetime import timedelta
import os, ast, json

os.environ
async def nostr_get(client: Client, filters: list, wait: int, connect: bool=True, disconnect: bool=True, relays_dict: dict=None, relays_list: list=None):
    """Get events from relays and return"""
    # init_logger(LogLevel.INFO)

    # Get default relays if needed
    if not relays_dict and not relays_list:
        relays_list = ast.literal_eval(os.getenv("DEFAULT_RELAYS"))

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

async def nostr_push(events: list[Event]=None, relays_dict: dict=None, relays_list: list=None):
    """Push Signed Events to relays"""
    # Get test_mode flag
    test_mode = os.getenv("TEST_MODE")

    # Get default relays if needed
    if not relays_dict and not relays_list:
        print("No relays provided loading default relays.")
        relays_list = ast.literal_eval(os.getenv("DEFAULT_RELAYS"))

    # Add and Connect to relays
    client = Client()
    if relays_dict is not None:
        for relay in relays_dict:
            if relays_dict[relay] in [None, "WRITE"]:
                    await client.add_relay(relay)
    else:
        for relay in relays_list:
            await client.add_relay(relay)

    # Post events except when in test mode.
    if test_mode != "Y":
        # init_logger(LogLevel.INFO)
        await client.connect()

        for event in events:
            if event.verify():
                await client.send_event(event)
            else:
                print(f"Unable to verify event: {event.as_json()}")

        await client.disconnect()
    else:
        print("TESTMODE: Event not posted.")
        for event in events:
            print(f"TESTMODE: {event.as_json()}")
        print("")

def nostr_prepare(eventbuilders: list[EventBuilder]=None):
    """Post event to relays"""
    # Get test_mode flag
    events_list = []
    if eventbuilders:
        test_mode = os.getenv("TEST_MODE")
        if test_mode == "Y":
            print("TESTMODE: Running in test mode, with dummy keys.")
            keys = Keys.parse(os.getenv("TEST_NSEC"))
        else:
            print("Generating random keys.")
            keys = Keys.generate()

        events_list = []
        for builder in eventbuilders:
            events_list.append(builder.to_event(keys).as_json())
    return json.dumps(events_list)