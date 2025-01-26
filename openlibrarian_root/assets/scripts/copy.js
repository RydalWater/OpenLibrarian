import { showEventToast } from './toast.js';

document.addEventListener('DOMContentLoaded', function() {
    const copyButtons = document.querySelectorAll('button[id^="copyButton"]');

    copyButtons.forEach(button => {
        button.addEventListener('click', async function(event) {
            event.preventDefault();
            const value = this.value;
            try {
                await navigator.clipboard.writeText(value);
                showEventToast({positive: true}, "Copied!");
            } catch (err) {
                console.error("Failed to copy text: ", err);
                showEventToast({positive: false}, "Unable to copy!");
            }
        });
    })
});
