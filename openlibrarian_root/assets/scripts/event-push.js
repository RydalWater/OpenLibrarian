const { Client, loadWasmAsync } = require("@rust-nostr/nostr-sdk");

// Define a function to push events, input will be signer, events and event_relays
async function pushEvents(signer, events, eventRelays, testMode = false) {
    if (testMode) {
        console.log("...");
        console.log("TESTMODE: Running in test mode.");
        console.log(`TESTMODE: Total Events=${events.length}`);
        console.log(`TESTMODE: Relays= ${eventRelays}`);
        for (let i = 0; i < events.length; i++) {
            console.log(`TESTMODE: Author=${events[i].author.toBech32()}`);
            console.log(`TESTMODE: Event=${events[i].asJson()}`);
            console.log(" ");
        }
        console.log("TESTMODE: Done.");
    } else {
        console.log("Pushing events to relays...");
        // Load the wasm
        await loadWasmAsync();
        // Set client with signer an authrization
        const client = new Client(signer);
        client.automaticAuthentication(); 

        // Add relays to client and connect individually
        for (let i = 0; i < eventRelays.length; i++) {
            client.addRelay(eventRelays[i]);
            try {
                await client.connectRelay(eventRelays[i]);
            } catch (e) {
                console.error("Error connecting to relay:", e);
            }
        }

        // Push events to relays
        for (let i = 0; i < events.length; i++) {
            try {
                await client.sendEvent(events[i]);
            } catch (e) {
                console.error("Error pushing event:", e);
            }
        }

        // Disconnect from relays
        await client.disconnect();
    }
}

// Export the function
export { pushEvents };
