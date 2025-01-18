const { Event, loadWasmAsync } = require("@rust-nostr/nostr-sdk");

async function parseEvent(event = null) {
    await loadWasmAsync();

    try {
        return Event.fromJson(event);
    } catch (e) {
        console.log(e);
        return null;
    }
}

module.exports = { parseEvent };