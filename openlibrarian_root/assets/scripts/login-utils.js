const { loadWasmSync, Keys, PublicKey } = require("@rust-nostr/nostr-sdk");

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

export { check_nsec, check_seed, check_npub_of_nsec };
