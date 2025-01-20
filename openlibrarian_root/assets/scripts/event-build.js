const { Keys, EventBuilder, Event, nip04Encrypt, loadWasmAsync, Tag } = require('@rust-nostr/nostr-sdk');

async function buildSignEvent(event = null, encrypt = null) {

    await loadWasmAsync();

    const nsec = localStorage.getItem("nsec")
    const keys = Keys.parse(nsec);
    // const keys = Keys.generate();

    if (event != null  && event instanceof Event) {
        // Extract element of event
        let tags = event.tags.asVec();
        let kind = event.kind;
        let content = ""

        // Look for :X: in the content
        const regex = /:(\d+):/;
        let match = event.content.match(regex);

        let contentPrefix, contentData;
        // Provided X > 0 split string into prefix and data
        if (match && parseInt(match[0].slice(1, -1)) > 0) {
            let index = match.index + match[0].length;
            contentPrefix = event.content.substring(0, index);
            contentData = event.content.substring(index);
        } else {
            contentPrefix = event.content;
            contentData = "";
            content = event.content;
        }

        // Encrypt the content if applicable
        if (encrypt) {
            let encrypted = nip04Encrypt(keys.secretKey, keys.publicKey, contentData);
            content = contentPrefix + encrypted;
        } else {
            content = contentPrefix + contentData;
        }

        // Rebuild event
        let builder = new EventBuilder(kind, content).tags(tags);

        // Sign the event
        let signedEvent = builder.signWithKeys(keys);

        // Return the signed event
        return signedEvent.asJson();

    } else {
        return null;
    }
}

module.exports = { buildSignEvent };