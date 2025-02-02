const { Keys, EventBuilder, loadWasmAsync } = require("@rust-nostr/nostr-sdk");
import { showEventToast } from './toast.js';
import { parseEvent } from './event-parse.js';

if (document.getElementById('conf-seed')) {
    const confSeed = document.getElementById('conf-seed');
    const tnpub = document.getElementById('tnpub');
    tnpub.value = localStorage.getItem('tnpub');

    confSeed.addEventListener('click', async function(event) {
        event.preventDefault();
        await loadWasmAsync();

        const seed = Array.from({ length: 12 }, (_, i) => document.getElementById(`word${i + 1}`).value.trim()).join(' ').toLowerCase();

        if (seed !== localStorage.getItem('tseed')) {
            try {
                const keys = Keys.fromMnemonic(seed);
                if (keys.publicKey.toBech32() !== localStorage.getItem('tnpub')) {
                    showEventToast({ positive: false }, "Seed does not match with NPUB. Please try again.");
                    return;
                }
            } catch (err) {
                showEventToast({ positive: false }, "Invalid seed. Please try again.");
                return;
            }
        }

        const keys = Keys.fromMnemonic(seed);
        localStorage.setItem('nsec', keys.secretKey.toBech32());
        localStorage.setItem('npub', keys.publicKey.toBech32());

        const payload = { npubValue: keys.publicKey.toBech32(), hasNsec: "Y" };
        const response = await fetch('/create_account_empty/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const responseData = await response.json();

        if (responseData.raw_events) {
            const events = JSON.parse(responseData.raw_events);
            const signedEvents = await Promise.all(events.map(async (event) => {
                const parsedEvent = await parseEvent(event);
                const builder = new EventBuilder(parsedEvent.kind, parsedEvent.content).tags(parsedEvent.tags.asVec());
                return builder.signWithKeys(keys).asJson();
            }));
            const response = await fetch('/event_publisher/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ events_json: JSON.stringify(signedEvents) })
            });
            const publisherResponse = await response.json();
            if (publisherResponse.event_message && publisherResponse.event_message.startsWith("Success:")) {
                showEventToast({ positive: true }, "Successfully set up account.");
                document.getElementById('confirm-box').style.display = 'none';
                document.getElementById('success-box').style.display = 'block';
            } else {
                showEventToast({ positive: false }, "Unable to complete sign-up with default relays.");
            }
        }
    });
}