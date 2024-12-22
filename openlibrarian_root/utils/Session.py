from asgiref.sync import sync_to_async
from django.core.cache import cache

# Sync Functions
def get_session_info(request: object) -> dict:
    """Returns the session information for the user."""
    return {
        'npub': request.session.get('npub', None),
        'nsec': request.session.get('nsec', None),
        'nym': request.session.get('nym', None),
        'profile': request.session.get('profile', None),
        'relays': request.session.get('relays', None),
        'mod_relays': request.session.get('mod_relays', None),
        'libraries': request.session.get('libraries', None),
        'interests': request.session.get('interests', None),
        'progress' : request.session.get('progress', None)
    }

def get_temp_keys(request: object) -> dict:
    """Returns the temp session information for the user signup."""
    return {
        'tnpub': request.session.get('tnpub', None),
        'tnsec': request.session.get('tnsec', None)
    }

def set_session_info(request: object, **kwargs):
    """Sets the session information for the user."""
    for key, value in kwargs.items():
        request.session[key] = value

def remove_session_info(request: object, **kwargs):
    """Removes the session information for the user."""
    for key in kwargs:
        request.session[key] = None

def logged_in(request: object) -> bool:
    """Checks if the user is logged in."""
    if request.session.get('npub', None) is not None:
        return True
    else:
        return False

# Async Functions
async def async_get_session_info(request: object) -> dict:
    """Convert get_session_info to async function."""
    return await sync_to_async(get_session_info)(request)

async def async_get_temp_keys(request: object) -> dict:
    """Convert get_temp_keys to async function."""
    return await sync_to_async(get_temp_keys)(request)

async def async_set_session_info(request: object, **kwargs):
    """Convert set_session_info to async function."""
    return await sync_to_async(set_session_info)(request, **kwargs)

async def async_remove_session_info(request: object, **kwargs):
    """Convert remove_session_info to async function."""
    return await sync_to_async(remove_session_info)(request, **kwargs)

async def async_logged_in(request: object) -> bool:
    """Convert logged_in to async function."""
    return await sync_to_async(logged_in)(request)

# Cache Functions
async def cache_key(type: str, session: dict) -> str:
    """Returns the session information for the user."""
    return f'{type}_{session["npub"]}'

async def cache_get(key: str) -> dict:
    """Returns the session information for the user."""
    return cache.get(key)

async def cache_set(key: str, value: dict, timeout=None):
    """Sets the session information for the user."""
    cache.set(key, value, timeout)

async def cache_delete(key: str):
    """Sets the session information for the user."""
    cache.delete(key)