import { showEventToast } from './toast.js';

// Check if "add-toast" element exists by id on page
if (document.getElementById('add-note')) {
    const addToast = document.getElementById('add-note');
    if (addToast.value != "None") {
        // Get value of "add-toast" element and split two values on ":" where value 1 is called note and value 2 is called option
        const [option, noteVal] = addToast.value.split(':');
        
        // Get postive option
        let optionVal;
        if (option == "false") {
            optionVal = {positive: false};
        } else {
            optionVal = {positive: true};
        }
        // Call showEventToast function with note and option values
        showEventToast(optionVal, noteVal);
    }
}