from nostr_sdk import EventBuilder, Tag
import os
import ast


# Notification function
async def build_notification(
    book: dict, note_type: str, text: str = None, tags: list = None, score: float = None
):
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
        if text is None or text == "":
            if ".0" in str(score):
                score = round(score)
            if note_type == "st":
                text = f"I just started reading '{title}' by {author} and I'm tracking my progress on www.OpenLibrarian.com \n "
            elif note_type == "en" and score:
                text = f"I just finished reading '{title}' by {author} and gave it {score} out of 5 stars! \n\n I tracked this on www.OpenLibrarian.com \n "
            elif note_type == "rv":
                text = f"I just reviewed '{title}' by {author} and gave it {score} out of 5 stars! \n\n I rated this on www.OpenLibrarian.com \n "
        elif text:
            if ".0" in str(score):
                score = round(score)
            if note_type == "rv":
                text = f"I just reviewed '{title}' by {author} and gave it {score} out of 5 stars! \n\n {text} \n\n I rated this on www.OpenLibrarian.com \n "
            else:
                # TODO: Handle custom text for start and end notes.
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
        build = EventBuilder.text_note(content=text).tags(h_tags)

        # Send event
        return build
