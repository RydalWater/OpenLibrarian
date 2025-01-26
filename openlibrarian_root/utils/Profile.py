from nostr_sdk import Client, Filter, Kind, Metadata, PublicKey, RelayMetadata, EventBuilder
from utils.Network import nostr_get
import os, ast


async def fetch_profile_info(relays:list|dict = None, npub: str = None):
    """Fetches the profile information from Nostr Default Relay."""
    # Check if relays is a dict
    drelays = None
    if relays:
        if type(relays) == dict:
            drelays = relays

    # Open client connection
    client = Client(None)

    # Get public key
    author = PublicKey.parse(npub)

    # Request profile Metadata
    f_meta = Filter().kind(Kind(0)).author(author).limit(1)
    metaevent = await nostr_get(client=client, relays_dict=drelays, filters=[f_meta], wait=10, disconnect=False)

    # If metadata is available extract relevant information
    if metaevent:
        metadata = Metadata.from_json(metaevent[0].content())
        nym_profile = {
            "nym": metadata.get_name(),
            "nip05": metadata.get_nip05(),
            "displayname": metadata.get_display_name(),
            "about": metadata.get_about(),
            "picture": metadata.get_picture(),
            "website": metadata.get_website(),
            "banner": metadata.get_banner(),
            "lud06": metadata.get_lud06(),
            "lud16": metadata.get_lud16()
        }
    else:
        nym_profile = {
            "nym": None,
            "nip05": None,
            "displayname": None,
            "about": None,
            "picture": None,
            "website": None,
            "banner": None,
            "lud06": None,
            "lud16": None
        }
    
    # Request check for relay metadata event
    f_relays = Filter().kind(Kind(10002)).author(author).limit(1)
    relays_event = await nostr_get(client=client, relays_dict=drelays, filters=[f_relays], wait=10, connect=False, disconnect=True)

    # If relays data is available extract relevant otherwise, use input or default relays.
    if relays_event:
        nym_relays = {}
        for tag in relays_event[0].tags():
            tagvec = tag.as_vec()
            if len(tagvec) == 3:
                url = tagvec[1]
                rw = tagvec[2].upper()
            else:
                url = tagvec[1]
                rw = None
            nym_relays[url] = rw
    else:
        if relays:
            if type(relays) == list:
                nym_relays = {relay: None for relay in relays}
            elif type(relays) == dict:
                nym_relays = relays
            else:
                nym_relays = None
        else:
            nym_relays = None
    
    # Make sure there is at least one read and one write relay if not add default relays
    has_read = False
    has_write = False
    if nym_relays:
        for each in nym_relays:
            if nym_relays[each] in [None]:
                has_read = True
                has_write = True
            else:
                if nym_relays[each] in ["READ"]:
                    has_read = True
                if nym_relays[each] in ["WRITE"]:
                    has_write = True

    if nym_relays == None or has_read is False or has_write is False:
        relays_list = ast.literal_eval(os.getenv("DEFAULT_RELAYS"))
        added_relays = True
        if nym_relays == None:
            nym_relays = {relay: None for relay in relays_list}
        else:
            for relay in relays_list:
                if relay not in nym_relays.keys():
                    nym_relays[relay] = None
    else:
        added_relays = False

    # Return profile information
    return nym_profile, nym_relays, added_relays


async def edit_profile_info(nym_profile: dict):
    """Updates the profile information using Relay List."""

    # Create profile event
    profile_meta = Metadata()
    if nym_profile["nym"] != None:
        profile_meta = profile_meta.set_name(nym_profile["nym"])
    if nym_profile["nip05"] != None:
        profile_meta = profile_meta.set_nip05(nym_profile["nip05"])
    if nym_profile["displayname"] != None:
        profile_meta = profile_meta.set_display_name(nym_profile["displayname"])
    if nym_profile["about"] != None:
        profile_meta = profile_meta.set_about(nym_profile["about"])
    if nym_profile["picture"] not in (None, ""):
        profile_meta = profile_meta.set_picture(nym_profile["picture"])
    if nym_profile["website"] not in (None, ""):
        profile_meta = profile_meta.set_website(nym_profile["website"])
    if nym_profile["banner"] not in (None, ""):
        profile_meta = profile_meta.set_banner(nym_profile["banner"])
    if nym_profile["lud06"] != None:
        profile_meta = profile_meta.set_lud06(nym_profile["lud06"])
    if nym_profile["lud16"] != None:
        profile_meta = profile_meta.set_lud16(nym_profile["lud16"])

    build = EventBuilder.metadata(profile_meta)

    return build


async def edit_relay_list(session_relays: dict, mod_relays: dict):
    """Updates the Relay List information."""
    update = False
    builder = None

    # Handle None
    if session_relays == None:
        session_relays = {}
    if mod_relays == None:
        # Set default session relays
        default_relays = ast.literal_eval(os.getenv("DEFAULT_RELAYS"))
        mod_relays = {}
        for relay in default_relays:
            mod_relays[relay] = None

    # Check for changes
    if len(session_relays) != len(mod_relays):
        update = True
    else:
        for relay in mod_relays:
            if relay not in session_relays.keys() or session_relays[relay] != mod_relays[relay]:
                update = True
                break

    # For updates construct event sign and publish
    if update:
        new_relays = {}
        for relay in mod_relays:
            if mod_relays[relay] == None:
                new_relays[relay] = None
            else:
                new_relays[relay] = RelayMetadata.READ if mod_relays[relay] == "READ" else RelayMetadata.WRITE

        # Builder
        builder = EventBuilder.relay_list(new_relays)

    return update, builder