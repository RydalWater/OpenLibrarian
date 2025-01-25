from nostr_sdk import EventBuilder, Tag
import os, ast


# Notification function
async def build_notification(book: dict, nym_relays: dict, note_type: str, text: str=None, tags: list=None, score: int=None):
    """Send notification to relays"""
    if note_type.lower() not in ["st", "en", "rv"]:
        raise Exception("Invalid note type.")
    else:
        note_type = note_type.lower()

        # Get book information
        if book["h"] == "Y":
            title = "A Mysterious Book"
            author = "an Unknown Author"
        else:
            title = book["t"]
            author = book["a"]

        # Construct event
        if text is None:
            if note_type == "st":
                text = f"I just started reading '{title}' by {author} and am tracking my progress on www.OpenLibrarian.com \n"
            elif note_type == "en" and score:
                text = f"I just finished reading '{title}' by {author} and gave it {score} out of 5 stars! \n\n I am tracking my progress on www.OpenLibrarian.com \n"
            elif note_type == "rv":
                text = f"I just reviewed '{title}' by {author} and gave it {score} out of 5 stars! \n\n I am tracking my ratings on www.OpenLibrarian.com \n"
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
                    text = f"{text} #{tag}"
                    h_tags.append(Tag.hashtag(tag))

        # Build event
        build = EventBuilder.text_note(content=text, tags=h_tags)

        # Send event
        return build
