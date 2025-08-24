from django.test import TestCase
from library_card.views import fetch_user_data
from circulation_desk.tests.test_index import TC_NPUB, TC_LIBRARIES
import hashlib


class FetchDataUnitTests(TestCase):
    """
    Test cases for the fetch_user_data function
    """

    def setUp(self):
        """
        Set Up
        """
        pass

    async def test_fetch_user_data(self):
        """
        Test the fetch_user_data function
        """
        (
            profile,
            relays,
            added_relays,
            libraries,
            interest_list,
            progress,
            reviews,
        ) = await fetch_user_data(TC_NPUB)

        self.assertEqual(None, profile["nym"])
        self.assertEqual(None, profile["displayname"])
        self.assertEqual(None, profile["about"])
        self.assertEqual(None, profile["picture"])
        self.assertEqual(None, profile["nip05"])
        self.assertEqual(None, profile["website"])
        self.assertEqual(None, profile["banner"])
        self.assertEqual(None, profile["lud06"])
        self.assertEqual(None, profile["lud16"])
        self.assertEqual(
            {
                "wss://relay.damus.io": None,
                "wss://relay.primal.net": None,
                "wss://nostr.mom": None,
            },
            relays,
        )
        self.assertEqual(True, added_relays)
        empty_libs = TC_LIBRARIES
        for lib in empty_libs:
            lib["b"] = []
            identifier_str = TC_NPUB + lib["s"]
            sha1 = hashlib.sha1()
            sha1.update(identifier_str.encode("utf-8"))
            lib["i"] = sha1.hexdigest()
        self.assertEqual(empty_libs, libraries)
        self.assertEqual([], interest_list)
        self.assertEqual({}, progress)
        self.assertEqual({}, reviews)

    def tearDown(self):
        """
        Tear Down
        """
        pass
