from nostr_sdk import Client, Filter, Kind, Metadata, PublicKey, Keys, NostrSigner, RelayMetadata, EventBuilder
from utils.Network import nostr_get, nostr_post, nostr_post_profile


async def fetch_profile_info(relays:list|dict = None, npub: str = None):
    """Fetches the profile information from Nostr Default Relay."""
    # Get defauilt relays

    # Open client connection
    client = Client(None)

    # Get public key
    author = PublicKey.parse(npub)

    # Request profile Metadata
    f_meta = Filter().kind(Kind(0)).author(author).limit(1)
    metaevent = await nostr_get(client=client, relays_dict=relays, filters=[f_meta], wait=10, disconnect=False)

    # If metadata is available extract relevant information
    if metaevent:
        metadata = Metadata.from_json(metaevent[0].content())
        nym_profile = {
            "nym": metadata.get_name(),
            "nip05": metadata.get_nip05(),
            "displayname": metadata.get_display_name(),
            "about": metadata.get_about(),
            "picture": metadata.get_picture(),
        }
    else:
        nym_profile = {
            "nym": None,
            "nip05": None,
            "displayname": None,
            "about": None,
            "picture": None,
        }

    # Request check for relay metadata event
    f_relays = Filter().kind(Kind(10002)).author(author).limit(1)
    relays_event = await nostr_get(client=client, relays_dict=relays, filters=[f_relays], wait=10, connect=False, disconnect=True)

    # If metadata is available extract relevant information and append default if none
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
            nym_relays = {relay: None for relay in relays}
        else:
            nym_relays = None

    # Return profile information
    return nym_profile, nym_relays


async def edit_profile_info(nym_profile: dict, nym_relays: dict, nsec: str):
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
    if nym_profile["picture"] != None:
        profile_meta = profile_meta.set_picture(nym_profile["picture"])

    # Instantiate client and set signer
    signer = NostrSigner.keys(Keys.parse(nsec))
    client = Client(signer)

    # Set the write relays
    await nostr_post_profile(client=client, profile_meta=profile_meta, relays_dict=nym_relays)


async def edit_relay_list(session_relays: dict, mod_relays: dict, nsec: str):
    """Updates the Relay List information."""
    update = False

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
        
        # Instantiate client and set signer
        signer = NostrSigner.keys(Keys.parse(nsec))
        client = Client(signer)

        # Builder
        eventbuilder = EventBuilder.relay_list(new_relays)

        # Post event
        await nostr_post(client=client, eventbuilder=eventbuilder, relays_dict=new_relays)