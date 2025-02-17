from nostr_sdk import Event, Tag, TagKind, EventBuilder, Kind, Client, Filter, PublicKey
from utils.Login import check_npub
from utils.Network import nostr_get
import hashlib


class Interests:
    """
    Interests Class. Allows for easy creation and access of list of interests.
    """
    def __init__(self, **kwargs):
        if "list" in kwargs.keys():
            if type(kwargs["list"]) != list:
                raise ValueError("List of interests must be of type list.")
            self.interests = kwargs["list"]
        elif "event" in kwargs.keys():
            if type(kwargs["event"]) != Event:
                raise ValueError("Event object must be of type nostr_sdk.Event.")
            event = kwargs["event"]
            interests = []
            for tag in event.tags().to_vec():
                if tag.as_vec()[0] == "t":
                    interests.append(tag.as_vec()[1]) 
            self.interests = interests
        else:
            self.interests = []
        self.bevent = None
    
    def compare_interests(self, interests: list):
        """Compare list of interests with list of interests"""
        if self.interests.sort() == interests.sort():
            return True
        else:
            # Modify self.interests
            self.interests = interests
            return False


    def build_event(self, npub: str = None):
        """Build event from library object"""
        # Events Kind and tags
        kind = Kind(30015)
        sha1 = hashlib.sha1()
        sha1.update(f"{npub}OLInterests".encode("utf-8"))
        tags = [
            Tag.identifier(sha1.hexdigest()),
            Tag.custom(TagKind.TITLE(),["OL Interests"]),
            Tag.custom(TagKind.DESCRIPTION(),["List of interests"]),
        ] 
        for interest in self.interests:
            tags.append(Tag.hashtag(interest))

        # Event content
        content = ""
        
        # Build event
        builder = EventBuilder(
            kind = kind,
            content = content
        ).tags(tags)

        self.bevent = builder

        return self

    def __dict__(self):
        return self.interests
    
async def fetch_interests(npub: str, nym_relays: dict):
    """Fetch interests from relays"""
    # Check if npub is valid
    if npub in [None, ""] or check_npub(npub) is False:
        raise Exception("No npub provided or invalid npub.")
    else:
        # Get identifier for event
        event_id = hashlib.sha1()
        event_id.update(f"{npub}OLInterests".encode("utf-8"))
        event_id = event_id.hexdigest()

        # Filter
        filter = Filter().author(PublicKey.parse(npub)).identifier(event_id).limit(10)

        # Instantiate client
        client = Client(None)

        # get events
        events = await nostr_get(client=client, wait=10, filters=filter, relays_dict=nym_relays)

        # Sort and take the latest
        events = sorted(events, key=lambda event: event.created_at().as_secs(), reverse=True)

        # Convert events to interests
        for event in events:
            if event.id() == event_id:
                interests = Interests(event=event)
                event_id = None
                break
        if event_id is not None:
            interests = Interests()

        return interests.__dict__()
