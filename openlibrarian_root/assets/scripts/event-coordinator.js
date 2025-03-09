import { showEventToast } from './toast.js';
import { parseEvent } from './event-parse.js';
import { buildSignEvent } from './event-build.js';
import { pushEvents } from './event-push.js';

// Wait for the DOM to load
document.addEventListener('DOMContentLoaded', async function() {
    // Check if the 'events' element has a value
    if (document.getElementById("events").value != "" && document.getElementById("events").value != null && document.getElementById("events").value != undefined && document.getElementById("events").value != "None") {
        try {
            // Parse the value as a JSON array
            const events = JSON.parse(document.getElementById("events").value);
            const eventRelays = document.getElementById("event_relays").value;
            const testMode = document.getElementById("test_mode").value === "true";
            console.log("Test Mode:", testMode);
            // Parse and sign each event
            const signedEvents = [];
            let signer = null;
            for (let i = 0; i < events.length; i++) {
                let parsed = await parseEvent(events[i]);
                let signed = null;
                let signing = null;
                if (parsed != null) {
                    // split list of event and signer
                    signing = await buildSignEvent(parsed, false);
                    signed = signing[0];
                    if (signer == null) {
                        signer = signing[1];
                    }
                }
                signedEvents.push(signed);
            }
            // Remove the value from the 'events' element
            document.getElementById("events").value = "";
   
            if (signedEvents.length > 0) {
                // Push the events
                await pushEvents(signer, signedEvents, eventRelays, testMode);
                showEventToast({positive:true}, "Updated."); 
            } else {
                showEventToast({positive:false}, "No events to update."); 
            }
        } catch (e) {
            showEventToast({positive:false}, "Error publishing events.");
            console.error("Error publishing events:", e);
        }
    }
});