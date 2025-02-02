// Check if we're on the login_nip07 page
if (window.location.href.indexOf("login-nip07") > -1) {
    // Check if user has installed NIP-07 extension
    if (window.nostr) {
        // User has NIP-07 installed
        document.getElementById('nip07-unavailable').classList.add('not-visible');
        document.getElementById('nip07-available').classList.remove('not-visible');

        const login = document.getElementById('login');
        login.disabled = false;
    } else {
        // User does not have NIP-07 installed
        document.getElementById('nip07-unavailable').classList.remove('not-visible');
        document.getElementById('nip07-available').classList.add('not-visible');
        document.getElementById('login').disabled = true;
    }
}