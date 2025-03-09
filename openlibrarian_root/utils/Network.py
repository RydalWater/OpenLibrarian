# Various functions to allow for quick maintaince of Nostr Network connections
from nostr_sdk import Client, Event, EventBuilder, Keys, Filter, Events, init_logger, LogLevel, UnsignedEvent
from datetime import timedelta
import os, ast, json, asyncio

os.environ
async def nostr_get(client: Client, filters: list | Filter, wait: int, connect: bool=True, disconnect: bool=True, relays_dict: dict=None, relays_list: list=None):
    """Get events from relays and return"""
    # init_logger(LogLevel.INFO)

    # Get default relays if needed
    if not relays_dict and not relays_list:
        relays_list = ast.literal_eval(os.getenv("DEFAULT_RELAYS"))

    # Add and Connect to relays
    relay_urls = []
    if relays_dict is not None:
        for relay in relays_dict:
            if relays_dict[relay] in [None, "READ"]:
                    await client.add_relay(relay)
                    relay_urls.append(relay)
    else:
        for relay in relays_list:
            await client.add_relay(relay)
            relay_urls.append(relay)
    
    if connect:
        await client.connect()

    # Get the events
    if wait:
        td = timedelta(seconds=wait)
    else:
        td = timedelta(seconds=15)
    
    if type(filters) == list:
        events = await asyncio.gather(*[client.fetch_events(filter=f, timeout=td) for f in filters])
    else:
        events = await client.fetch_events(filter=filters, timeout=td)

    # Disconnect
    if disconnect:
        await client.disconnect()

    # Return
    return events.to_vec()

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
            events_list.append(builder.sign_with_keys(keys).as_json())
    return json.dumps(events_list)

def get_event_relays(relays_dict: dict=None, relays_list: list=None, rw: str="WRITE"):
    """Get relays for pushing events return list of relay urls"""
    if relays_dict:
        relays_list = []
        for relay in relays_dict:
            if relays_dict[relay] in [None, rw]:
                relays_list.append(relay)

    if relays_list in (None, []):
        relays_list = ast.literal_eval(os.getenv("DEFAULT_RELAYS"))
    
    return relays_list