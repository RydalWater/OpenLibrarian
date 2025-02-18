import { showEventToast } from './toast.js';
import { parseEvent } from './event-parse.js';
import { buildSignEvent } from './event-build.js';

// Wait for the DOM to load
document.addEventListener('DOMContentLoaded', async function() {
    // Check if the 'events' element has a value
    if (document.getElementById("events").value != "" && document.getElementById("events").value != null && document.getElementById("events").value != undefined && document.getElementById("events").value != "None") {
        try {
            // Parse the value as a JSON array
            const events = JSON.parse(document.getElementById("events").value);
            // Parse and sign each event
            const signedEvents = [];
            for (let i = 0; i < events.length; i++) {
                let parsed = await parseEvent(events[i]);
                let signed = null;
                if (parsed != null) {
                    signed = await buildSignEvent(parsed, false);
                }
                signedEvents.push(signed);
            }
            // Remove the value from the 'events' element
            document.getElementById("events").value = "";
            // Convert signedEvents to Json String
            let signedEventsJson = JSON.stringify(signedEvents);
            // Fetch event publisher
            const response = await fetch('/event_publisher/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({'events_json': signedEventsJson})
            });
            const data = await response.json();
            if (data.event_message != null) {
                // Check if data.message starts with "Success:"
                if (data.event_message.startsWith("Success:")) {
                    // Remove "Success:" from data.message
                    document.getElementById('event-notification').value = data.event_message.slice(8);
                    showEventToast({positive:true}); 
                } else {
                    document.getElementById('event-notification').value = data.event_message;
                    showEventToast({positive:false}); 
                }
            }
        } catch (e) {
            console.error("Error parsing events:", e);
        }
    }
});