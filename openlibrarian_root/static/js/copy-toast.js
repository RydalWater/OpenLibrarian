const copyButtons = document.querySelectorAll('button[id^="copyButton"]');

copyButtons.forEach(button => {
    button.addEventListener('click', function(event) {
        event.preventDefault();

        const value = this.value;
        const textarea = document.createElement('textarea');
        textarea.value = value;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);

        const toastContainer = document.getElementById('copytoastContainer');
        const toast = document.createElement('div');
        toast.classList.add('toast', 'align-items-center', 'text-white', 'bg-success', 'border-0');
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.innerHTML = `
            <div class="toast-body">
                Copied!
            </div>
        `;

        toastContainer.appendChild(toast);
        const toastElement = new bootstrap.Toast(toast);
        toastElement.show();

        setTimeout(function() {
            toastElement.hide();
        }, 2000);
    });
});
