import { check_nsec, check_seed } from "./login-utils.js";
import { showEventToast } from './toast.js';
import { parseEvent } from './event-parse.js';
import { getCsrfToken } from "./get-cookie.js";
const { loadWasmAsync, Keys, EventBuilder, nip04Decrypt } = require("@rust-nostr/nostr-sdk");

// Declare variables outside of if blocks
let nsec = null;
let seed = null;
let login = null;

// Check if nsec/words and submit exist on the page
if (document.getElementById('nsec')) {
    nsec = document.getElementById('nsec');
}

if (document.getElementById('login')) {
    login = document.getElementById('login');
}

if (document.getElementById('word1')) {
    seed = document.getElementById('word1');
}

if ((nsec != null || seed != null) && login != null) {
    login.addEventListener('click', async function(event) {    
        event.preventDefault();        
        let result = false;
        let keys = null;
        let seedValue = "";
        let nsecValue = "";

        // Check valid nsec/seed
        if (nsec != null) {
            nsecValue = nsec.value;
            result = check_nsec(nsecValue);
        } else {
            for (let i = 1; i <= 12; i++) {
                const element = document.getElementById(`word${i}`);
                if (element) {
                    seedValue += " " + element.value;
                }
            }
            seedValue = seedValue.trim();
            console.log(seedValue);
            // Check the seed has 12 words
            result = check_seed(seedValue);
        }
        // Execute Login Actions 
        if (result) {
            // Load WASM
            loadWasmAsync();
            if (nsec != null) {
                keys = Keys.parse(nsecValue);
            } else {
                keys = Keys.fromMnemonic(seedValue);
            }
            let npubValue = keys.publicKey.toBech32();
            // Set session Nsec
            localStorage.setItem('nsec', nsecValue);
            // Set session Npub
            localStorage.setItem('npub', npubValue);
            // Set payload and call backend
            let payload = {'npubValue': npubValue, 'hasNsec': "Y"}
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
            // Execute the login-nsec view with events
            payload.decryptedEvents = decryptedEvents;
            let csrf = getCsrfToken();
            fetch('/login-nsec/', {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf
                },
                body: JSON.stringify(payload)
            })
            .then(response => response.json())
            .then(data => {
                if (data.error_message) {
                    document.getElementById('event-notification').value = "Invalid NSEC";
                    showEventToast({positive:false}); 
                }
                if (data.redirect) {
                    window.location.href = data.redirect;
                }
            });
        } else {
            // Set error message
            if (nsec != null) {
                document.getElementById('event-notification').value = "Invalid NSEC";
            } else {
                // Set error message
                document.getElementById('event-notification').value = "Invalid Seed";
            }
            showEventToast({positive:false}); 
        }
    });
}