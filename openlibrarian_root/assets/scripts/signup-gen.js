const { Keys, loadWasmAsync } = require("@rust-nostr/nostr-sdk");
import { generateMnemonic } from '@scure/bip39';
import { wordlist } from '@scure/bip39/wordlists/english';

if (document.getElementById('seed-gen')) {
    const seedGen = document.getElementById('seed-gen');

    seedGen.addEventListener('click', async function(event) {
        event.preventDefault();
        await loadWasmAsync();

        // Clear local storage and generate new seed and keys
        localStorage.clear();
        const tseed = generateMnemonic(wordlist);
        const tkeys = Keys.fromMnemonic(tseed);
        const tnpub = tkeys.publicKey.toBech32();
        const tnsec = tkeys.secretKey.toBech32();

        // Store new values in local storage
        localStorage.setItem('tnsec', tnsec);
        localStorage.setItem('tnpub', tnpub);
        localStorage.setItem('tseed', tseed);

        // Update UI
        document.getElementById('info-box').style.display = 'none';
        document.getElementById('key-box').style.display = 'block';

        // Update HTML elements with retrieved values
        document.getElementById('tnpub').value = tnpub;
        document.getElementById('tnsec').value = tnsec;

        // Update input elements with word values
        const words = tseed.split(' ');
        words.forEach((word, i) => {
            document.getElementById(`tword${i + 1}`).value = word;
        });

        // Add event handler for save-seed button
        document.getElementById('save-seed').addEventListener('click', function(event) {
            event.preventDefault();
            window.location.href = '/create-account-confirm/';
        });
    });
}