const { loadWasmSync, loadWasmAsync, Keys, PublicKey, NostrConnectURI } = require("@rust-nostr/nostr-sdk");

function check_nsec(nsec) {
    loadWasmSync();
    try {
        Keys.parse(nsec);
        return true;
    } catch (e) {
        return false;
    }
}

function check_seed(seed) {
    loadWasmSync();
    if (seed.split(" ").length == 12) {
        try {
            Keys.fromMnemonic(seed);
            return true;
        } catch (e) {
            console.log(e);
            return false;
        }
    } else {
        return false;
    }
}

function check_npub_of_nsec(npub, nsec) {
    try {
        let pub = PublicKey.parse(npub);
        let keys = Keys.parse(nsec);
        if (keys.publicKey.toBech32() == pub.toBech32()) {
            return true;
        } else {
            return false;
        }
    } catch (e) {
        return false;
    }
}

// Function to check if localStorage are empty and if so redirect to login page
function checkLocalStorage() {
    if (localStorage.getItem("nsec") == null || localStorage.getItem("npub") == null) {
        if (localStorage.getItem("nsec")) {
            localStorage.removeItem("nsec");
        } else if (localStorage.getItem("npub")) {
            localStorage.removeItem("npub");
        }
        // Clear backend session data using logout view
        return fetch('/logout/', {
            method: 'POST'
        });
    }
    return Promise.resolve();
}

async function check_uri(uri) {
    await loadWasmAsync();
    try {
        NostrConnectURI.parse(uri);
        return true;
    } catch (e) {
        return false;
    }
}

export { check_nsec, check_seed, check_npub_of_nsec, checkLocalStorage, check_uri };
