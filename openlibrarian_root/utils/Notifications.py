from nostr_sdk import EventBuilder, Keys, NostrSigner, Client, Tag
from utils.Login import check_nsec
from utils.Network import nostr_post
import os, ast


# Notification function
async def send_notification(book: dict, nsec: str, nym_relays: dict, note_type: str, text: str=None, tags: list=None, score: int=None):
    """Send notification to relays"""
    if nsec in [None, ""] or check_nsec(nsec) is False:
        raise Exception("No nsec provided or invalid nsec.")
    elif note_type.lower() not in ["st", "en", "rv"]:
        raise Exception("Invalid note type.")
    else:
        note_type = note_type.lower()

        # Instantiate client and set signer
        signer = NostrSigner.keys(Keys.parse(nsec))
        client = Client(signer)

        # Get book information
        if book["h"] == "Y":
            title = "Mysterious Book"
            author = "Unknown Author"
        else:
            title = book["t"]
            author = book["a"]

        # Construct event
        if text is None:
            if note_type == "st":
                text = f"I just started reading '{title}' by {author} and am tracking my progress on www.OpenLibrarian.com"
            elif note_type == "en" and score:
                text = f"I just finished reading '{title}' by {author} and gave it {score} out of 5 stars! \n\n I am tracking my progress on www.OpenLibrarian.com"
            elif note_type == "en" and score:
                text = f"I just finished reading '{title}' by {author}. \n\n I am tracking my progress on www.OpenLibrarian.com"
            elif note_type == "rv":
                text = f"I just reviewed '{title}' by {author} and gave it {score} out of 5 stars! \n\n I am tracking my ratings on www.OpenLibrarian.com"
        elif text:
            # TODO: Add ability for users to change their notification message text. 
            pass
            
        # Tags
        h_tags = []
        if tags:
            # TODO: Dynamically pull book category tags.
            pass
        else:
            d_tags = ast.literal_eval(os.getenv("DEFAULT_TAGS"))
            if d_tags:
                for tag in d_tags:
                    h_tags.append(Tag.hashtag(tag))

        # Build event
        event = EventBuilder.text_note(content=text, tags=h_tags)

        # Send event
        await nostr_post(client=client, eventbuilder=event, relays_dict=nym_relays)
