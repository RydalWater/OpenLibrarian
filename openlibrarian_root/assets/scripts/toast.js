function showEventToast(options, note){
  // Use provided value of note if available 
  const notificationInput = document.getElementById('event-notification');
  let notification = notificationInput.value;
  if (note) {
    notification = note;
  }
  const positive = options.positive !== undefined ? options.positive : true;

  if (notification && notification !== "None") {
    const toastContainer = document.getElementById('event-toastContainer');
    const toast = document.createElement('div');
    toast.classList.add('toast', 'align-items-center', 'text-white', 'bg-success', 'border-0');
    if (!positive) {
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
}

export { showEventToast };