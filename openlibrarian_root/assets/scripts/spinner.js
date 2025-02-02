// Check if required elements exist
if (document.getElementById('spinnerBox') && document.querySelector('form')) {
    const spinnerBox = document.getElementById('spinnerBox');
    const form = document.querySelector('form');
    const dataBox = document.getElementById('dataBox');

    // Show spinnerBox and hide dataBox on form submit or specific button clicks
    const showSpinner = () => {
        spinnerBox.classList.remove("not-visible");
        if (dataBox) dataBox.classList.add("not-visible");
    };

    form.addEventListener('submit', showSpinner);
    document.addEventListener('click', (event) => {
        if (['login', 'refresh', 'submit-search', 'refresh-simple'].includes(event.target.id)) {
            showSpinner();
        }
    });

    // Hide spinnerBox and show dataBox on AJAX response
    document.addEventListener('ajax:complete', (event) => {
        if (event.detail.method === 'POST') {
            spinnerBox.classList.add("not-visible");
            if (dataBox) dataBox.classList.remove("not-visible");
        }
    });
}