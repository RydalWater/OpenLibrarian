// Detect if we're on the logout or card page
if (window.location.href.indexOf("logout") > -1 || window.location.href.indexOf("card") > -1) {
    // Remove locally stored items
    localStorage.removeItem("nsec");
    localStorage.removeItem("npub");
}

// Set up listeners for Explore and New buttons on card page
if (window.location.href.indexOf("card") > -1) {
    ['explore', 'new'].forEach(id => {
        const button = document.getElementById(id);
        if (button) {
            button.addEventListener('click', () => {
                localStorage.removeItem("nsec");
                localStorage.removeItem("npub");
            });
        }
    });
}