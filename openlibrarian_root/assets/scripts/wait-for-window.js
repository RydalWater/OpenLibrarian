// Function to wait for window.nostr
const { Nip07Signer } = require("@rust-nostr/nostr-sdk");

async function waitForNostr() {
    const startTime = Date.now();
    while (!window.nostr && Date.now() - startTime < 5000) {
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    if (window.nostr) {
        return new Nip07Signer(window.nostr);
    } else {
        throw new Error("NIP-07 not available");
    }
}

export { waitForNostr };