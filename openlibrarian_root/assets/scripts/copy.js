import { showEventToast } from './toast.js';

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('button[id^="copyButton"]').forEach(button => {
        button.addEventListener('click', async event => {
            event.preventDefault();
            try {
                await navigator.clipboard.writeText(button.value);
                showEventToast({ positive: true }, "Copied!");
            } catch (err) {
                console.error("Failed to copy text: ", err);
                showEventToast({ positive: false }, "Unable to copy!");
            }
        });
    });
});