import { check_nsec, check_seed } from "./login-utils.js";
import { showEventToast } from './toast.js';
import { parseEvent } from './event-parse.js';
import { getCsrfToken } from "./get-cookie.js";
const { loadWasmSync, loadWasmAsync, Keys, EventBuilder, nip04Decrypt, Nip07Signer, NostrSigner } = require("@rust-nostr/nostr-sdk");


// Declare variables outside of if blocks
let nsec = null;
let seed = null;
let nip07 = null;
let login = null;

// Check if nsec/words/nip07 and login exist on the page
if (document.getElementById('nsec')) {
    nsec = document.getElementById('nsec');
}

if (document.getElementById('word1')) {
    seed = document.getElementById('word1');
}

if (window.location.href.indexOf("login-nip07") > -1) {
    nip07 = true;
}

if (document.getElementById('login')) {
    login = document.getElementById('login');
}

if ((nsec != null || seed != null || nip07) && login != null) {
    login.addEventListener('click', async function(event) {    
        event.preventDefault();        
        let result = false;
        let keys = null;
        let pubKey = null;
        let seedValue = "";
        let nsecValue = "";
        let npubValue = "";
        let signer = null;

        if (nsec != null) {
            // Check valid nsec
            nsecValue = nsec.value;
            result = check_nsec(nsecValue);
        } else if (seed != null) {
            // Check valid seed 
            for (let i = 1; i <= 12; i++) {
                const element = document.getElementById(`word${i}`);
                if (element) {
                    seedValue += " " + element.value;
                }
            }
            seedValue = seedValue.trim();
            result = check_seed(seedValue);
        } else if (nip07) {
            // Check valid nip07
            try {
                loadWasmSync();
                signer = new Nip07Signer(window.nostr);
                result = true;
            } catch (e) {
                console.log("Issue with NIP-07");
            }            
        }
        // Execute Login Actions 
        if (result) {
            // Load WASM
            loadWasmAsync();
            if (nsec != null) {
                keys = Keys.parse(nsecValue);
            } else if (seed != null) {
                keys = Keys.fromMnemonic(seedValue);
            } else if (nip07) {
                pubKey = await signer.getPublicKey();
            }

            if (keys) {
                npubValue = keys.publicKey.toBech32();
                // Set session Nsec
                localStorage.setItem('nsec', keys.secretKey.toBech32());
            } else {
                npubValue = pubKey.toBech32();
                // Set session Nsec
                localStorage.setItem('nsec', 'signer');
            }
            
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
            } else if (seed != null) {
                document.getElementById('event-notification').value = "Invalid Seed";
            } else {
                document.getElementById('event-notification').value = "Invalid NIP07";
            }
            showEventToast({positive:false}); 
        }
    });
}