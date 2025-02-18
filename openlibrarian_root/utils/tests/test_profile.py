from django.test import TestCase
import os, ast, asyncio
from datetime import timedelta
from utils.Profile import fetch_profile_info, edit_profile_info, edit_relay_list
from nostr_sdk import Keys

TC_NPUB1 = "npub1039j8zfxafe5xtx5qhmjf02rv7upgwgx54kd35e5qehj36egkjuqx9f704"
TC_NPUB2 = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
TC_NSEC2 = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
TC_RELAYS = {"wss://relay.damus.io": None, "wss://nostr.mom": None}


class ProfileUnitTests(TestCase):
    def setUp(self):
        pass
    
    async def test_fetch_profile_nometa(self):
        """
        Test the fetch_profile function (empty metadata)
        """
        profile, relays, added_relays = await fetch_profile_info(npub=TC_NPUB2, relays=TC_RELAYS)
        self.assertEqual(profile["nym"], None)
        self.assertEqual(profile["nip05"], None)
        self.assertEqual(profile["displayname"], None)
        self.assertEqual(profile["about"], None)
        self.assertEqual(profile["picture"], None)
        self.assertEqual(profile["website"], None)
        self.assertEqual(profile["banner"], None)
        self.assertEqual(profile["lud06"], None)
        self.assertEqual(profile["lud16"], None)        
        self.assertEqual(relays, TC_RELAYS)
        self.assertEqual(added_relays, False)
    
    async def test_fetch_profile_withmeta(self):
        """
        Test the fetch_profile function (with metadata)
        """
        profile, relays, added_relays = await fetch_profile_info(npub=TC_NPUB1, relays=TC_RELAYS)
        self.assertEqual(profile["nym"], "Violet")
        self.assertEqual(profile["nip05"], "")
        self.assertEqual(profile["displayname"], "Violet")
        self.assertEqual(profile["about"], "Purple by name purple by nature, a bit bookish!!")
        self.assertEqual(profile["picture"], "https://pfp.nostr.build/9d45acc985222226824a1e91850bf3d450b8b5964ef14f41fbd4df2c9dcc3241.jpg")
        self.assertEqual(profile["website"], None)
        self.assertEqual(profile["banner"], None)
        self.assertEqual(profile["lud06"], None)
        self.assertEqual(profile["lud16"], None)
        # Sort relays by alphabetical keys for consistency
        relays = dict(sorted(relays.items()))
        test_relays = {'wss://nos.lol/': 'WRITE', 'wss://nostr.mom/': None, 'wss://relay.damus.io/': None, 'wss://relay.primal.net/': None}
        self.assertEqual(relays, test_relays)
        self.assertEqual(added_relays, False)
    
    async def test_fetch_profile_norelays(self):
        """
        Test the fetch_profile function (no relays)
        """
        profile, relays, added_relays = await fetch_profile_info(npub=TC_NPUB2, relays=None)
        self.assertEqual(profile["nym"], None)
        self.assertEqual(profile["nip05"], None)
        self.assertEqual(profile["displayname"], None)
        self.assertEqual(profile["about"], None)
        self.assertEqual(profile["picture"], None)
        self.assertEqual(profile["website"], None)
        self.assertEqual(profile["banner"], None)
        self.assertEqual(profile["lud06"], None)
        self.assertEqual(profile["lud16"], None)
        self.assertEqual(relays, {'wss://relay.damus.io': None, 'wss://relay.primal.net': None, 'wss://nos.lol': None, 'wss://nostr.mom': None})
        self.assertEqual(added_relays, True)
    
    async def test_fetch_profile_nowriterelays(self):
        """
        Test the fetch_profile function (with no write relays dict input)
        """
        profile, relays, added_relays = await fetch_profile_info(npub=TC_NPUB2, relays={'wss://nos.lol': 'READ'})
        self.assertEqual(profile["nym"], None)
        self.assertEqual(profile["nip05"], None)
        self.assertEqual(profile["displayname"], None)
        self.assertEqual(profile["about"], None)
        self.assertEqual(profile["picture"], None)
        self.assertEqual(profile["website"], None)
        self.assertEqual(profile["banner"], None)
        self.assertEqual(profile["lud06"], None)
        self.assertEqual(profile["lud16"], None)        
        self.assertEqual(relays, {'wss://nos.lol': 'READ', 'wss://relay.damus.io': None, 'wss://relay.primal.net': None, 'wss://nostr.mom': None})
        self.assertEqual(added_relays, True)
    
    async def test_fetch_profile_listrelays(self):
        """
        Test the fetch_profile function (with list relays input)
        """
        profile, relays, added_relays = await fetch_profile_info(npub=TC_NPUB2, relays=['wss://nos.lol'])
        self.assertEqual(profile["nym"], None)
        self.assertEqual(profile["nip05"], None)
        self.assertEqual(profile["displayname"], None)
        self.assertEqual(profile["about"], None)
        self.assertEqual(profile["picture"], None)
        self.assertEqual(profile["website"], None)
        self.assertEqual(profile["banner"], None)
        self.assertEqual(profile["lud06"], None)
        self.assertEqual(profile["lud16"], None)        
        self.assertEqual(relays, {'wss://nos.lol': None})
        self.assertEqual(added_relays, False)

    async def test_fetch_profile_strrelays(self):
        """
        Test the fetch_profile function (with string relays input)
        """
        profile, relays, added_relays = await fetch_profile_info(npub=TC_NPUB2, relays='wss://nos.lol')
        self.assertEqual(profile["nym"], None)
        self.assertEqual(profile["nip05"], None)
        self.assertEqual(profile["displayname"], None)
        self.assertEqual(profile["about"], None)
        self.assertEqual(profile["picture"], None)
        self.assertEqual(profile["website"], None)
        self.assertEqual(profile["banner"], None)
        self.assertEqual(profile["lud06"], None)
        self.assertEqual(profile["lud16"], None)        
        self.assertEqual(relays, {'wss://relay.damus.io': None, 'wss://relay.primal.net': None, 'wss://nos.lol': None, 'wss://nostr.mom': None})
        self.assertEqual(added_relays, True)
        
    async def test_edit_profile(self):
        """
        Test the edit_profile function
        """
        profile, relays, added_relays = await fetch_profile_info(npub=TC_NPUB2, relays=TC_RELAYS)
        keys = Keys.parse(TC_NSEC2)
        # Update the profile nym
        profile["nym"] = "TestProfile"
        builder = await edit_profile_info(nym_profile=profile)
        event = builder.sign_with_keys(keys)
        self.assertEqual(event.content(), '{"name":"TestProfile"}')
        
        # Update the profile nip05
        profile["nym"] = None
        profile["nip05"] = "test.nip05@nostr.test"
        builder = await edit_profile_info(nym_profile=profile)
        event = builder.sign_with_keys(keys)
        self.assertEqual(event.content(), '{"nip05":"test.nip05@nostr.test"}')

        # Update the profile displayname
        profile["nip05"] = None
        profile["displayname"] = "TestDisplayname"
        builder = await edit_profile_info(nym_profile=profile)
        event = builder.sign_with_keys(keys)
        self.assertEqual(event.content(), '{"display_name":"TestDisplayname"}')

        # Update the profile about
        profile["displayname"] = None
        profile["about"] = "TestAbout"
        builder = await edit_profile_info(nym_profile=profile)
        event = builder.sign_with_keys(keys)
        self.assertEqual(event.content(), '{"about":"TestAbout"}')

        # Update the profile picture
        profile["about"] = None
        profile["picture"] = "https://somepicture.com/picture.jpg"
        builder = await edit_profile_info(nym_profile=profile)
        event = builder.sign_with_keys(keys)
        self.assertEqual(event.content(), '{"picture":"https://somepicture.com/picture.jpg"}')

        # Update the profile website
        profile["picture"] = None
        profile["website"] = "https://somewebsite.com"
        builder = await edit_profile_info(nym_profile=profile)
        event = builder.sign_with_keys(keys)
        self.assertEqual(event.content(), '{"website":"https://somewebsite.com/"}')

        # Update the profile banner
        profile["website"] = None
        profile["banner"] = "https://somebanner.com"
        builder = await edit_profile_info(nym_profile=profile)
        event = builder.sign_with_keys(keys)
        self.assertEqual(event.content(), '{"banner":"https://somebanner.com/"}')

        # Update the profile lud06
        profile["banner"] = None
        profile["lud06"] = "test.lud06@nostr.test"
        builder = await edit_profile_info(nym_profile=profile)
        event = builder.sign_with_keys(keys)
        self.assertEqual(event.content(), '{"lud06":"test.lud06@nostr.test"}')

        # Update the profile lud16
        profile["lud06"] = None
        profile["lud16"] = "test.lud16@nostr.test"
        builder = await edit_profile_info(nym_profile=profile)
        event = builder.sign_with_keys(keys)
        self.assertEqual(event.content(), '{"lud16":"test.lud16@nostr.test"}')

        # Combine all
        profile["nym"] = "TestProfile"
        profile["nip05"] = "test.nip05@nostr.test"
        profile["displayname"] = "TestDisplayname"
        profile["about"] = "TestAbout"
        profile["picture"] = "https://somepicture.com/picture.jpg"
        profile["website"] = "https://somewebsite.com"
        profile["banner"] = "https://somebanner.com"
        profile["lud06"] = "test.lud06@nostr.test"
        profile["lud16"] = "test.lud16@nostr.test"
        builder = await edit_profile_info(nym_profile=profile)
        event = builder.sign_with_keys(keys)
        self.assertEqual(event.content(), '{"name":"TestProfile","display_name":"TestDisplayname","about":"TestAbout","website":"https://somewebsite.com/","picture":"https://somepicture.com/picture.jpg","banner":"https://somebanner.com/","nip05":"test.nip05@nostr.test","lud06":"test.lud06@nostr.test","lud16":"test.lud16@nostr.test"}')
    
    async def test_edit_relay_list_none_session(self):
        """
        Test the edit_relay_list function (none session relays)
        """
        keys = Keys.parse(TC_NSEC2)
        update, builder = await edit_relay_list(session_relays=None, mod_relays=TC_RELAYS)
        event = builder.sign_with_keys(keys)
        self.assertEqual(update, True)
        for relay in TC_RELAYS:
            self.assertIn('["r","'+relay,event.as_json())
    
    async def test_edit_relay_list_none_mod(self):
        """
        Test the edit_relay_list function (none mod relays)
        """
        keys = Keys.parse(TC_NSEC2)
        update, builder = await edit_relay_list(session_relays=TC_RELAYS, mod_relays=None)
        event = builder.sign_with_keys(keys)
        default_relays = ast.literal_eval(os.getenv("DEFAULT_RELAYS"))
        self.assertEqual(update, True)
        for relay in default_relays:
            self.assertIn('["r","'+relay,event.as_json())

    async def test_edit_relay_list_no_update(self):
        """
        Test the edit_relay_list function (no updates)
        """
        update, builder = await edit_relay_list(session_relays=TC_RELAYS, mod_relays=TC_RELAYS)
        self.assertEqual(update, False)
        self.assertEqual(builder, None)
    
    async def test_edit_relay_list_update_same_len(self):
        """
        Test the edit_relay_list function (updates with same length)
        """
        keys = Keys.parse(TC_NSEC2)
        update, builder = await edit_relay_list(session_relays=TC_RELAYS, mod_relays={'wss://relay.primal.net/': None})
        event = builder.sign_with_keys(keys)
        self.assertEqual(update, True)
        self.assertIn('["r","wss://relay.primal.net/"]',event.as_json())
        
    async def test_edit_relay_list_update_diff_len(self):
        """
        Test the edit_relay_list function (updates with different length)
        """
        keys = Keys.parse(TC_NSEC2)
        update, builder = await edit_relay_list(session_relays={}, mod_relays={'wss://relay.primal.net/': "READ", 'wss://nostr.mom/': "WRITE", 'wss://relay.damus.io/': None, 'wss://relay.test/': "BUG"})
        event = builder.sign_with_keys(keys)
        self.assertEqual(update, True)
        self.assertIn('["r","wss://relay.primal.net/","read"]',event.as_json())
        self.assertIn('["r","wss://nostr.mom/","write"]',event.as_json())
        self.assertIn('["r","wss://relay.damus.io/"]',event.as_json())
        self.assertIn('["r","wss://relay.test/","write"]',event.as_json())


    def tearDown(self):
        pass