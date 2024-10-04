from nostr_sdk import Event, Tag, TagKind, EventBuilder, Keys, Kind, NostrSigner, Client, Filter, PublicKey
from utils.Login import check_npub, check_nsec
from utils.Network import nostr_get, nostr_post
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
            for tag in event.tags():
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


    def build_event(self, npub: str = None, nsec: str = None):
        """Build event from library object"""
        if not self._validate_npub_and_nsec(npub, nsec):
            raise Exception("Invalid npub or nsec.")

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
            tags = tags,
            content = content
        )

        self.bevent = builder

        return self
    
    async def publish_event(self, nym_relays: dict[str, str] = None, nsec: str = None):
        """Publish event from Interests object"""
        if not self._validate_npub_and_nsec(None, nsec):
            raise Exception("Invalid nsec.")
        if self.bevent is None:
            raise Exception("Missing required information.")

        # Instantiate client and set signer
        signer = NostrSigner.keys(Keys.parse(nsec))
        client = Client(signer)

        # Post event
        try:
            await nostr_post(client=client, eventbuilder=self.bevent, relays_dict=nym_relays)
            return "Published event."

        except Exception as e:
            raise Exception(f"Unable to publish event: {e}")


    def _validate_npub_and_nsec(self, npub: str, nsec: str) -> bool:
        if npub is not None and (npub in [None, ""] or check_npub(npub) is False):
            return False
        if nsec is not None and (nsec in [None, ""] or check_nsec(nsec) is False):
            return False
        return True

    def __dict__(self):
        return self.interests
    
async def fetch_interests(npub: str, nym_relays: dict):
    """Fetch interests from relays"""
    # Check if npub and nsec are valid
    if npub in [None, ""] or check_npub(npub) is False:
        raise Exception("No npub provided or invalid npub.")
    else:
        # Get identifier for event
        event_id = hashlib.sha1()
        event_id.update(f"{npub}OLInterests".encode("utf-8"))
        event_id = event_id.hexdigest()

        # Filter
        filter = Filter().author(PublicKey.from_bech32(npub)).identifier(event_id).limit(10)

        # Instantiate client
        client = Client(None)

        # get events
        events = await nostr_get(client=client, wait=10, filters=[filter], relays_dict=nym_relays)

        # Sort and take the latest
        events = sorted(events, key=lambda event: event.created_at().as_secs(), reverse=True)

        # Convert events to interests
        for event in events:
            if event.identifier() == event_id:
                interests = Interests(event=event)
                event_id = None
                break
        if event_id is not None:
            interests = Interests()

        return interests.__dict__()
