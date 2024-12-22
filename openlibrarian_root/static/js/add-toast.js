const notificationInput = document.getElementById('notification');
const notification = notificationInput.value;

if (notification && notification !== "None") {
    const toastContainer = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.classList.add('toast', 'align-items-center', 'text-white', 'bg-success', 'border-0');
    if (notification === "Book already in library." || notification === "Already Following." || notification === "Invalid npub or nip05." || notification === "Please provide npub or nip05." || notification === "Current progress is greater than max." || notification === "End date is before start date.") {
        toast.classList.remove('bg-success');
        toast.classList.add('bg-danger');
    }
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.innerHTML = `
        <div class="toast-body">
            ${notification}
        </div>
    `;

    toastContainer.appendChild(toast);
    const toastElement = new bootstrap.Toast(toast);
    toastElement.show();

    setTimeout(function() {
        toastElement.hide();
    }, 2000);
}