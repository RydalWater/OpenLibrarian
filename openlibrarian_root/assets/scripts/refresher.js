import { check_nsec } from "./login-utils.js";
import { showEventToast } from './toast.js';
import { parseEvent } from './event-parse.js';
import { getCsrfToken } from "./get-cookie.js";
const { loadWasmAsync, Keys, EventBuilder, nip04Decrypt } = require("@rust-nostr/nostr-sdk");

// Declare variables outside of if blocks
let refresh = null;
let refreshSimple = null;
let refreshVal = null;

// Check if refresh and submit exist on the page
if (document.getElementById('refresh')) {
    refresh = document.getElementById('refresh');
    refreshVal = refresh.value;
}

if (refresh != null) {
    refresh.addEventListener('click', async function(event) {    
        event.preventDefault();
        // Deactivate the refresh button
        refresh.disabled = true;
        let result = false;
        let keys = null;
        let nsecValue = localStorage.getItem('nsec');

        // Check valid nsec/seed
        result = check_nsec(nsecValue);

        // Execute Login Actions 
        if (result) {
            // Load WASM
            loadWasmAsync();
            keys = Keys.parse(nsecValue);

            let npubValue = keys.publicKey.toBech32();

            // Set payload and call backend
            let payload = {'npubValue': npubValue, 'hasNsec': "Y", 'refresh': refreshVal}
            // Fetch event publisher
            const response = await fetch('/fetch_events/', {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            let decryptedEvents = [];
            const data = await response.json();
            if (data.raw_events != null) {
                // Parse raw events as json array
                let events = JSON.parse(data.raw_events);
                for (let i = 0; i < events.length; i++) {
                    let event = await parseEvent(events[i]);
                    // Extract element of event decrypt content and rebuild event
                    let tags = event.tags.asVec();
                    let kind = event.kind;
                    let content = "";

                    // Look for :X: in the content
                    const regex = /:\d+:/;
                    let match = event.content.match(regex);
                    
                    let contentPrefix, contentData;
                    // Provided X > 0 split string into prefix and data
                    if (match && parseInt(match[0].slice(1, -1)) > 0) {
                        let index = match.index + match[0].length;
                        contentPrefix = event.content.substring(0, index);
                        contentData = event.content.substring(index);
                        let decryptedContent = "";
                        if (contentData != "") {
                            decryptedContent = nip04Decrypt(keys.secretKey, keys.publicKey, contentData);
                        }
                        content = contentPrefix + decryptedContent;
                    } else {
                        contentPrefix = event.content;
                        contentData = "";
                        content = event.content;
                    }
                    // Rebuild event
                    let builder = new EventBuilder(kind, content).tags(tags);
            
                    // Sign the event
                    let signedEvent = builder.signWithKeys(keys);

                    // Add event to array
                    decryptedEvents.push(signedEvent.asJson());
                }
            }
            // Execute the library/shelves view with events
            payload.decryptedEvents = decryptedEvents;
            let csrf = getCsrfToken();
            await fetch('/library/shelves/', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf
              },
              body: JSON.stringify(payload)
            })
            .then(response => {
                // Check if dataBox and spinnerBox exist and if so trigger show, hide respectively
                if (document.getElementById('dataBox')) {
                    document.getElementById('dataBox').classList.remove("not-visible");
                }
                if (document.getElementById('spinnerBox')) {
                    document.getElementById('spinnerBox').classList.add("not-visible");
                }
                // Then pop some toasts
                if (data.message != "") {
                    showEventToast({positive: true}, "Refreshed");
                }
                // Reactivate the refresh button
                refresh.disabled = false;

                // Delay the page reload for 0.75 second
                setTimeout(() => {
                    window.location.href = window.location.href;
                }, 750);
            })
            .catch(error => {
              console.error('Error:', error);
            });
            
        }
    });
}