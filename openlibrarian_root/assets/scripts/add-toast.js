import { showEventToast } from './toast.js';

const addToast = document.getElementById('add-note');
if (addToast && addToast.value !== "None") {
    const [option, noteVal] = addToast.value.split(':');
    showEventToast({ positive: option !== "false" }, noteVal);
}