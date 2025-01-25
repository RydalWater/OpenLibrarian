// Detect if we're on the logout page
if (window.location.href.indexOf("logout") > -1) {
    // Remove the locally stored items
    localStorage.removeItem("nsec");
    localStorage.removeItem("npub");
}