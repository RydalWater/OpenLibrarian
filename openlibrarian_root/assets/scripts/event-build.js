const { Keys, PublicKey, EventBuilder, Event, nip04Encrypt, loadWasmAsync, NostrSigner } = require('@rust-nostr/nostr-sdk');
import { checkLocalStorage } from "./login-utils.js";
import { waitForNostr } from "./wait-for-window.js";

async function buildSignEvent(event = null, encrypt = null) {

    await checkLocalStorage();

    loadWasmAsync();

    const nsec = localStorage.getItem("nsec");
    let keys = null;
    let pubKey = null;
    let signer = null;
    if (nsec == "signer-nip07")  {
        signer = NostrSigner.nip07(await waitForNostr());
    } else {
        signer = NostrSigner.keys(Keys.parse(nsec));
    }
    pubKey = PublicKey.parse(localStorage.getItem("npub"));
    
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
            // Set encrypt to true if X > 0
            encrypt = true;
        } else {
            contentPrefix = event.content;
            contentData = "";
            content = event.content;
        }

        // Encrypt the content if applicable
        if (encrypt) {
            let encrypted = "";
            if (signer) { 
                encrypted = await signer.nip04Encrypt(pubKey, contentData);
            } else {
                encrypted = nip04Encrypt(keys.secretKey, keys.publicKey, contentData);
            }
            content = contentPrefix + encrypted;
        } else {
            content = contentPrefix + contentData;
        }

        // Rebuild event
        let builder = new EventBuilder(kind, content).tags(tags);

        // Sign the event
        let signedEvent = null;
        signedEvent = await builder.sign(signer);

        // Return the signed event and signer
        return [signedEvent, signer];
    } else {
        return [null, null];
    }
}

export { buildSignEvent };