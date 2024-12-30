from django.test import TestCase
import io, sys, os, ast
from utils.Profile import fetch_profile_info, edit_profile_info, edit_relay_list

TC_NPUB1 = "npub1039j8zfxafe5xtx5qhmjf02rv7upgwgx54kd35e5qehj36egkjuqx9f704"
TC_NPUB2 = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
TC_NSEC2 = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
TC_RELAYS = {"wss://relay.damus.io": None}

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
        
        # Update the profile nym
        profile["nym"] = "TestProfile"
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        await edit_profile_info(nym_profile=profile,nsec=TC_NSEC2,nym_relays=TC_RELAYS)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        self.assertEqual(output.split("\n")[2], 'TESTMODE: {"name":"TestProfile"}')

        # Update the profile nip05
        profile["nym"] = None
        profile["nip05"] = "test.nip05@nostr.test"
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        await edit_profile_info(nym_profile=profile,nsec=TC_NSEC2,nym_relays=TC_RELAYS)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        self.assertEqual(output.split("\n")[2], 'TESTMODE: {"nip05":"test.nip05@nostr.test"}')

        # Update the profile displayname
        profile["nip05"] = None
        profile["displayname"] = "TestDisplayname"
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        await edit_profile_info(nym_profile=profile,nsec=TC_NSEC2,nym_relays=TC_RELAYS)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        self.assertEqual(output.split("\n")[2], 'TESTMODE: {"display_name":"TestDisplayname"}')

        # Update the profile about
        profile["displayname"] = None
        profile["about"] = "TestAbout"
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        await edit_profile_info(nym_profile=profile,nsec=TC_NSEC2,nym_relays=TC_RELAYS)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        self.assertEqual(output.split("\n")[2], 'TESTMODE: {"about":"TestAbout"}')

        # Update the profile picture
        profile["about"] = None
        profile["picture"] = "https://somepicture.com/picture.jpg"
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        await edit_profile_info(nym_profile=profile,nsec=TC_NSEC2,nym_relays=TC_RELAYS)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        self.assertEqual(output.split("\n")[2], 'TESTMODE: {"picture":"https://somepicture.com/picture.jpg"}')

        # Update the profile website
        profile["picture"] = None
        profile["website"] = "https://somewebsite.com"
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        await edit_profile_info(nym_profile=profile,nsec=TC_NSEC2,nym_relays=TC_RELAYS)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        self.assertEqual(output.split("\n")[2], 'TESTMODE: {"website":"https://somewebsite.com/"}')

        # Update the profile banner
        profile["website"] = None
        profile["banner"] = "https://somebanner.com"
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        await edit_profile_info(nym_profile=profile,nsec=TC_NSEC2,nym_relays=TC_RELAYS)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        self.assertEqual(output.split("\n")[2], 'TESTMODE: {"banner":"https://somebanner.com/"}')

        # Update the profile lud06
        profile["banner"] = None
        profile["lud06"] = "test.lud06@nostr.test"
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        await edit_profile_info(nym_profile=profile,nsec=TC_NSEC2,nym_relays=TC_RELAYS)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        self.assertEqual(output.split("\n")[2], 'TESTMODE: {"lud06":"test.lud06@nostr.test"}')

        # Update the profile lud16
        profile["lud06"] = None
        profile["lud16"] = "test.lud16@nostr.test"
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        await edit_profile_info(nym_profile=profile,nsec=TC_NSEC2,nym_relays=TC_RELAYS)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        self.assertEqual(output.split("\n")[2], 'TESTMODE: {"lud16":"test.lud16@nostr.test"}')

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
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        await edit_profile_info(nym_profile=profile,nsec=TC_NSEC2,nym_relays=TC_RELAYS)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        expected = 'TESTMODE: {"name":"TestProfile","display_name":"TestDisplayname","about":"TestAbout","website":"https://somewebsite.com/","picture":"https://somepicture.com/picture.jpg","banner":"https://somebanner.com/","nip05":"test.nip05@nostr.test","lud06":"test.lud06@nostr.test","lud16":"test.lud16@nostr.test"}'
        self.assertEqual(output.split("\n")[2], expected)
    
    async def test_edit_relay_list_none_session(self):
        """
        Test the edit_relay_list function (none session relays)
        """
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        update = await edit_relay_list(session_relays=None, mod_relays=TC_RELAYS, nsec=TC_NSEC2)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        self.assertEqual(update, True)
        self.assertIn('["r","wss://relay.damus.io/"]',output.split("\n")[2])
    
    async def test_edit_relay_list_none_mod(self):
        """
        Test the edit_relay_list function (none mod relays)
        """
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        update = await edit_relay_list(session_relays=TC_RELAYS, mod_relays=None, nsec=TC_NSEC2)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        self.assertEqual(update, True)
        default_relays = ast.literal_eval(os.getenv("DEFAULT_RELAYS"))
        for relay in default_relays:
            self.assertIn('["r","'+relay+'/"]',output.split("\n")[2])

    async def test_edit_relay_list_no_update(self):
        """
        Test the edit_relay_list function (no updates)
        """
        update = await edit_relay_list(session_relays=TC_RELAYS, mod_relays=TC_RELAYS, nsec=TC_NSEC2)
        self.assertEqual(update, False)
    
    async def test_edit_relay_list_update_same_len(self):
        """
        Test the edit_relay_list function (updates with same length)
        """
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        update = await edit_relay_list(session_relays=TC_RELAYS, mod_relays={'wss://relay.primal.net/': None}, nsec=TC_NSEC2)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        self.assertEqual(update, True)
        self.assertIn('["r","wss://relay.primal.net/"]',output.split("\n")[2])
    
    async def test_edit_relay_list_update_diff_len(self):
        """
        Test the edit_relay_list function (updates with different length)
        """
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        update = await edit_relay_list(session_relays={}, mod_relays={'wss://relay.primal.net/': "READ", 'wss://nostr.mom/': "WRITE", 'wss://relay.damus.io/': None, 'wss://relay.test/': "BUG"}, nsec=TC_NSEC2)
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        self.assertEqual(update, True)
        self.assertIn('["r","wss://relay.primal.net/","read"]',output.split("\n")[2])
        self.assertIn('["r","wss://nostr.mom/","write"]',output.split("\n")[2])
        self.assertIn('["r","wss://relay.damus.io/"]',output.split("\n")[2])
        self.assertIn('["r","wss://relay.test/","write"]',output.split("\n")[2])


    def tearDown(self):
        pass