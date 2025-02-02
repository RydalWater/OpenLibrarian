import { check_nsec } from "./login-utils.js";
import { showEventToast } from './toast.js';
import { parseEvent } from './event-parse.js';
import { getCsrfToken } from "./get-cookie.js";

const { loadWasmSync, loadWasmAsync, Keys, PublicKey, EventBuilder, Nip07Signer, NostrSigner, nip04Decrypt } = require("@rust-nostr/nostr-sdk");

// Declare variables outside of if blocks
const refreshButton = document.getElementById('refresh');
let refreshValue = null;

// Check if refresh and submit exist on the page
if (refreshButton) {
    refreshValue = refreshButton.value;

    refreshButton.addEventListener('click', async function(event) {    
        event.preventDefault();
        // Deactivate the refresh button
        refreshButton.disabled = true;
        const nsecValue = localStorage.getItem('nsec');
        const npubValue = localStorage.getItem('npub');
        let result = false;
        let keys = null;
        let pubKey = null;
        let signer = null;

        // Check valid nsec
        if (nsecValue == "signer") {
            loadWasmSync();
            signer = new Nip07Signer(window.nostr);
            pubKey = PublicKey.parse(npubValue);
            result = true;
        } else {
            result = check_nsec(nsecValue);
        }

        // Execute Login Actions 
        if (result) {
            // Load WASM
            loadWasmAsync();
            if (signer == null) {
                keys = Keys.parse(nsecValue);
            }

            // Set payload and call backend
            let payload = {'npubValue': npubValue, 'hasNsec': "Y", 'refresh': refreshValue}
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
                            if (signer) {
                                decryptedContent = await signer.nip04Decrypt(pubKey, contentData);
                            } else {
                                decryptedContent = nip04Decrypt(keys.secretKey, keys.publicKey, contentData);
                            }
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
                    let signedEvent = null;
                    if (signer) {
                        signedEvent = await builder.sign(NostrSigner.nip07(signer));
                    } else {
                        signedEvent = builder.signWithKeys(keys);
                    }

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
                refreshButton.disabled = false;

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