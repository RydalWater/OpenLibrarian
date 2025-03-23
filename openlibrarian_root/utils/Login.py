from nostr_sdk import PublicKey, Keys, NostrConnectUri
from mnemonic import Mnemonic

def check_npub(npub: str) -> bool:
    """Check if public key is valid."""
    try:
        PublicKey.parse(npub)
        return True
    except:
        return False

def check_nsec(nsec: str) -> bool:
    """Check if private key is valid."""
    try:
        Keys.parse(nsec)
        return True
    except:
        return False

def check_npub_of_nsec(npub: str, nsec: str) -> bool:
    """Check if public is valid for private key."""
    try:
        pub = PublicKey.parse(npub)
        keys = Keys.parse(nsec)
        if keys.public_key() == pub:
            return True
        else:
            return False
    except:
        return False

def check_mnemonic(mnemonic: str) -> bool:
    """Check if mnemonic is valid."""
    if len(mnemonic.split(" ")) != 12:
        return False

    return Mnemonic('english').check(mnemonic)

def check_nip46(bunker: str) -> bool:
    """Check if nip46 key is valid."""
    try:
        NostrConnectUri.parse(bunker)

        return True
    except:
        return False