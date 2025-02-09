// Check if we're on the login_nip07 page
if (window.location.href.indexOf("login-nip07") > -1) {
  // Wait for window.nostr to be available
  const nostrInterval = setInterval(() => {
    if (window.nostr) {
      clearInterval(nostrInterval);
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
  }, 100); // Check every 100ms
}