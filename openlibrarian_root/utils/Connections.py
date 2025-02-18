from nostr_sdk import Client, Filter, Kind, KindStandard, Metadata, PublicKey, EventBuilder, get_nip05_profile, Tag
from utils.Network import nostr_get
from utils.Login import check_npub

FOLLOW_KIND = Kind.from_std(KindStandard.CONTACT_LIST)
MUTE_KIND = Kind.from_std(KindStandard.MUTE_LIST)

async def fetch_social_list(relays: dict, npub: str = None, list_type: str = "follow"):
    """Fetches the following/muted list Events."""
    # Get Public Key from Npub
    if npub in [None, ""] or check_npub(npub) is False:
            raise Exception("Invalid or missing npub")
    public_key = PublicKey.parse(npub)
    
    # Open client connection with read relays
    client = Client(None)
    try:
        # Request profile Metadata
        if list_type == "follow":
            kind = FOLLOW_KIND
        elif list_type == "mute":
            kind = MUTE_KIND
        follow_filter = Filter().kind(kind).author(public_key).limit(1)

        eventlist = await nostr_get(client=client, filters=follow_filter, relays_dict=relays, wait=10, connect=True, disconnect=False)

        # If following_list event available extract relevant information
        follow_list = []
        if eventlist:
            for tag in eventlist[0].tags().to_vec():
                if tag.as_vec()[0] == "p":
                        if check_npub(tag.content()):
                            follow_list.append(PublicKey.parse(tag.content()))
                            
        # Get following and related profile data
        f = Filter().kind(Kind(0)).authors(follow_list)
        profiles = await nostr_get(client=client, relays_dict=relays, filters=f, wait=10, connect=False, disconnect=True)

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

async def clone_follow(relays: dict, npub: str = None):
    """Clones the following list and the muted list to new npub."""

    # Get Public Key from Npub
    if npub in [None, ""] or check_npub(npub) is False:
            raise Exception("Invalid or missing npub")
    
    # Keys
    clone_key = PublicKey.parse(npub)
    
    # Client
    client = Client(None)

    # Request profile Metadata
    follow_clone_filter = Filter().kind(FOLLOW_KIND).author(clone_key).limit(1)
    follow_filter = Filter().kind(FOLLOW_KIND).author(PublicKey.parse(npub)).limit(1)
    mute_clone_filter = Filter().kind(MUTE_KIND).author(clone_key).limit(1)
    mute_filter = Filter().kind(MUTE_KIND).author(PublicKey.parse(npub)).limit(1)


    # Get following list and extract p tags
    follow_events = await nostr_get(client=client, filters=[follow_clone_filter,follow_filter], relays_dict=relays, wait=10, connect=True, disconnect=False) 
    mute_events = await nostr_get(client=client, filters=[mute_clone_filter,mute_filter], relays_dict=relays, wait=10, connect=False, disconnect=False)

    follow_tags = []
    for follow in follow_events:
        for tag in follow.tags().to_vec():
            if tag not in follow_tags and tag.as_vec()[0] == "p":
                follow_tags.append(tag)

    mute_tags = []
    for mute in mute_events:
        for tag in mute.tags().to_vec():
            if tag not in mute_tags and tag.as_vec()[0] == "p":
                mute_tags.append(tag)


    # Build mute and follow events
    follow_builder = EventBuilder(kind=FOLLOW_KIND, tags=follow_tags, content="")
    mute_builder = EventBuilder(kind=MUTE_KIND, tags=mute_tags, content="")

    return [follow_builder, mute_builder]
    
    
async def add_follow(relays: dict, npub: str = None, follow_id: str = None):
    """Adds new npub to follow list."""
    if npub in [None, ""] or check_npub(npub) is False:
        raise Exception("Invalid or missing npub")
    if follow_id in [None, ""]:
        raise Exception("Missing follow value")
    
    # Check if follow is a valid pubkey or nip05 and get key
    if check_npub(follow_id) is True:
        follow_key = PublicKey.parse(follow_id)
    else:
        try:
            profile = await get_nip05_profile(follow_id,None)
            follow_key = profile.public_key()
        except:
           return "false:Invalid npub or nip05.", None
        
    # Request profile Metadata
    follow_filter = Filter().kind(FOLLOW_KIND).author(PublicKey.parse(npub)).limit(1)

    # Get following list and extract p tags
    client = Client(None)
    follow_events = await nostr_get(client=client, filters=follow_filter, relays_dict=relays, wait=10, connect=True, disconnect=False) 

    if follow_events in (None, []):
        tag = Tag.public_key(follow_key)
        build = EventBuilder(kind=FOLLOW_KIND, content="").tags([tag])
        return None, build
    else:
        for follow in follow_events:
            follow_tags = follow.tags()
            if Tag.public_key(follow_key) not in follow_tags:
                follow_tags.append(Tag.public_key(follow_key))

                # Build follow event
                build = EventBuilder(kind=FOLLOW_KIND, content="").tags(follow_tags)

                return None, build
            
            else:
                return "false:Already Following.", None
    
async def remove_follow(relays: dict, npub: str = None, follow_id: str = None):
    """Adds npub to follow list."""
    if npub in [None, ""] or check_npub(npub) is False:
        raise Exception("Invalid or missing npub")
    if follow_id in [None, ""]:
        raise Exception("Missing follow value")
    
    # Check if follow is a valid pubkey or nip05 and get key
    if check_npub(follow_id) is True:
        follow_key = PublicKey.parse(follow_id)
    else:
        return "false:Invalid npub.", None
        
    # Request profile Metadata
    follow_filter = Filter().kind(FOLLOW_KIND).author(PublicKey.parse(npub)).limit(1)

    # Get following list and extract p tags
    client = Client(None)
    follow_events = await nostr_get(client=client, filters=follow_filter, relays_dict=relays, wait=10, connect=True, disconnect=False) 

    if follow_events in (None, []):
        return "false:Not Following.", None
    else:
        for follow in follow_events:
            follow_tags = follow.tags()

            if Tag.public_key(follow_key) in follow_tags:
                follow_tags.remove(Tag.public_key(follow_key))

                # Build follow event
                build = EventBuilder(kind=FOLLOW_KIND, tags=follow_tags, content="")
                return None, build
            
            else:
                return "false:Not Following.", None    