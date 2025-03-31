const { Keys, NostrConnectURI, NostrConnect, NostrSigner, Duration, initLogger, LogLevel } = require("@rust-nostr/nostr-sdk");

async function nip46Connect(localBunker, localAppKeys) {
    initLogger(LogLevel.info());
    // App keys
    let appKeys = Keys.parse(localAppKeys);

    // Remote signer (NIP46)
    let uri = NostrConnectURI.parse(localBunker);
    let timeout = Duration.fromSecs(60);
    let connect = new NostrConnect(uri, appKeys, timeout);
    return NostrSigner.nip46(connect);
}

// Export the function
export { nip46Connect };
