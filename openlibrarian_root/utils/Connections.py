from nostr_sdk import Client, Filter, Kind, KindEnum, Metadata, PublicKey, TagKind, SingleLetterTag, Alphabet, Keys, NostrSigner, EventBuilder, Contact
from utils.Network import nostr_get, nostr_post
from utils.Login import check_npub, check_nsec

async def fetch_social_list(relays: dict, npub: str = None, list_type: str = "follow"):
    """Fetches the following/muted list Events."""
    # Get Public Key from Npub
    if npub in [None, ""] or check_npub(npub) is False:
            raise Exception("Invalid or missing npub")
    public_key = PublicKey.from_bech32(npub)
    
    # Open client connection with read relays
    client = Client(None)
    try:
        # Request profile Metadata
        if list_type == "follow":
            kind = Kind.from_enum(KindEnum.CONTACT_LIST())
        elif list_type == "mute":
            kind = Kind.from_enum(KindEnum.MUTE_LIST())
        follow_filter = Filter().kind(kind).author(public_key).limit(1)

        eventlist = await nostr_get(client=client, filters=[follow_filter], relays_dict=relays, wait=10, connect=True, disconnect=False)

        # If following_list event available extract relevant information
        follow_list = []
        if eventlist:
            for tag in eventlist[0].tags():
                follow_list.append(PublicKey.from_hex(tag.content()))

        # Get following and related profile data
        f = Filter().kind(Kind(0)).authors(follow_list)
        profiles = await nostr_get(client=client, relays_dict=relays, filters=[f], wait=10, connect=False, disconnect=True)

        # Extract names/image/npub
        social_list = {}
        for profile in profiles:
            pk_hex = profile.author().to_hex()
            pk_npub = profile.author().to_bech32()
            metadata = Metadata.from_json(profile.content())
            name = metadata.get_display_name()
            if name in (None, ""):
                name = metadata.get_name()
            if name in (None, ""):
                name = "Mystery Character"
            social_list[pk_hex] = {"npub": pk_npub, "image": metadata.get_picture(), "name": name}

        # Return list
        return social_list

    except Exception as e:
        print(e)
        return None

async def clone_follow(relays: dict, npub: str = None, nsec: str = None):
    """Clones the following list and the muted list to new npub."""

    # Get Public Key from Npub
    if npub in [None, ""] or check_npub(npub) is False:
            raise Exception("Invalid or missing npub")
    if nsec in [None, ""] or check_nsec(nsec) is False:
            raise Exception("Invalid or missing nsec")
    
    # Keys
    clone_key = PublicKey.from_bech32(npub)
    keys = Keys.parse(nsec)
    
    # Signer
    signer = NostrSigner.keys(keys)
    client = Client(signer)

    # Request profile Metadata
    follow_clone_filter = Filter().kind(Kind.from_enum(KindEnum.CONTACT_LIST())).author(clone_key).limit(1)
    follow_filter = Filter().kind(Kind.from_enum(KindEnum.CONTACT_LIST())).author(keys.public_key()).limit(1)
    mute_clone_filter = Filter().kind(Kind.from_enum(KindEnum.MUTE_LIST())).author(clone_key).limit(1)
    mute_filter = Filter().kind(Kind.from_enum(KindEnum.MUTE_LIST())).author(keys.public_key()).limit(1)


    # Get following list and extract p tags
    follow_events = await nostr_get(client=client, filters=[follow_clone_filter,follow_filter], relays_dict=relays, wait=10, connect=True, disconnect=False) 
    mute_events = await nostr_get(client=client, filters=[mute_clone_filter,mute_filter], relays_dict=relays, wait=10, connect=False, disconnect=False)

    follow_tags = []
    for follow in follow_events:
        for tag in follow.tags():
            if tag not in follow_tags and tag.as_vec()[0] == "p":
                follow_tags.append(tag)

    mute_tags = []
    for mute in mute_events:
        for tag in mute.tags():
            if tag not in mute_tags and tag.as_vec()[0] == "p":
                mute_tags.append(tag)


    # Build mute and follow events
    follow_builder = EventBuilder(kind=Kind.from_enum(KindEnum.CONTACT_LIST()), tags=follow_tags, content="")
    mute_builder = EventBuilder(kind=Kind.from_enum(KindEnum.MUTE_LIST()), tags=mute_tags, content="")

    # Post events
    await nostr_post(client=client, relays_dict=relays, eventbuilder=follow_builder, connect=False, disconnect=False)
    await nostr_post(client=client, relays_dict=relays, eventbuilder=mute_builder, connect=False, disconnect=True)
    
    


