# Various functions to allow for quick maintaince of Nostr Network connections
from nostr_sdk import Client, EventBuilder, Keys
from datetime import timedelta
import os
import ast
import json


async def nostr_get(
    filters: dict, wait: int, relays_dict: dict = None, relays_list: list = None
):
    """Get events from relays and return"""
    # init_logger(LogLevel.INFO)

    # Get relays list
    fetch_relays = get_event_relays(
        relays_dict=relays_dict, relays_list=relays_list, rw="WRITE"
    )

    # Start client
    client = Client(None)

    # Add relays and connect
    for relay in json.loads(fetch_relays):
        await client.add_relay(relay)
    await client.connect()

    # Get events for each filter can create a combined list
    if wait:
        td = timedelta(seconds=wait)
    else:
        td = timedelta(seconds=15)
    events = {}
    for key, f in filters.items():
        fetched = await client.fetch_events(filter=f, timeout=td)
        if fetched:
            events[key] = fetched.to_vec()

    # Disconnect
    await client.disconnect()

    # Return
    return events


def nostr_prepare(eventbuilders: list[EventBuilder] = None):
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


def get_event_relays(
    relays_dict: dict = None, relays_list: list = None, rw: str = "WRITE"
):
    """Get relays for pushing events return list of relay urls"""
    if relays_dict:
        relays_list = []
        for relay in relays_dict:
            if relays_dict[relay] in [None, rw]:
                relays_list.append(relay)

    if relays_list in (None, []):
        relays_list = ast.literal_eval(os.getenv("DEFAULT_RELAYS"))

    return json.dumps(relays_list)
