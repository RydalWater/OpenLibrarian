// Function to wait for window.nostr
const { NostrSigner, BrowserSigner } = require("@rust-nostr/nostr-sdk");

async function waitForNostr() {
    const startTime = Date.now();
    while (!window.nostr && Date.now() - startTime < 5000) {
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    if (window.nostr) {
        return NostrSigner.nip07(new BrowserSigner(window.nostr));
    } else {
        throw new Error("NIP-07 not available");
    }
}

export { waitForNostr };