// Detect if we're on the logout page
if (window.location.href.indexOf("logout") > -1) {
    // Remove the locally stored items
    localStorage.removeItem("nsec");
    localStorage.removeItem("npub");
} else if (window.location.href.indexOf("card") > -1) {
    // Set up listener for Explore button
    if (document.getElementById('explore')) {
        document.getElementById('explore').addEventListener('click', function(event) {
            localStorage.removeItem("nsec");
            localStorage.removeItem("npub");
            console.log(localStorage);
        });
    }
    // Set up listner for new button
    if (document.getElementById('new')) {
        document.getElementById('new').addEventListener('click', function(event) {
            localStorage.removeItem("nsec");
            localStorage.removeItem("npub");
        });
    }
}