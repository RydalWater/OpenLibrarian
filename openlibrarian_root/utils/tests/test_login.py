from django.test import TestCase
from utils.Login import check_npub, check_nsec, check_npub_of_nsec, check_mnemonic
from circulation_desk.tests.test_index import TC_NPUB, TC_NSEC


# Unit Test Cases
class LoginUnitTests(TestCase):
    def setUp(self):
        pass

    def test_check_npub(self):
        """
        Test Invalid NPUB value
        """
        npub = "npubmadeup123456blahblah"
        self.assertFalse(check_npub(npub))

    def test_check_npub_valid(self):
        """
        Test Valid NPUB value
        """
        npub = TC_NPUB
        self.assertTrue(check_npub(npub))

    def test_check_nsec(self):
        """
        Test Invalid NSEC value
        """
        nsec = "nsecmadeup123456blahblah"
        self.assertFalse(check_nsec(nsec))

    def test_check_nsec_valid(self):
        """
        Test Valid NSEC value
        """
        nsec = TC_NSEC
        self.assertTrue(check_nsec(nsec))

    def test_check_npub_of_nsec(self):
        """
        Test Invalid NSEC value
        """
        nsec = TC_NSEC
        npub = "npub1039j8zfxafe5xtx5qhmjf02rv7upgwgx54kd35e5qehj36egkjuqx9f704"
        self.assertFalse(check_npub_of_nsec(npub, nsec))

        npub = ""
        self.assertFalse(check_npub_of_nsec(npub, nsec))

    def test_check_npub_of_nsec_valid(self):
        """
        Test Valid NPUB of NSEC value
        """
        nsec = TC_NSEC
        npub = TC_NPUB
        self.assertTrue(check_npub_of_nsec(npub, nsec))

    def test_check_mnemonic_invalid(self):
        """
        Test Invalid Mnemonic values
        """
        mnemonic = "apple banana cherry date egg fig grape honey ice juice kiwi lemon"
        self.assertFalse(check_mnemonic(mnemonic))

        mnemonic = "apple banana cherry date egg fig grape honey ice juice kiwi"
        self.assertFalse(check_mnemonic(mnemonic))

        mnemonic = (
            "apple banana cherry date egg fig grape honey ice juice kiwi lemon mango"
        )
        self.assertFalse(check_mnemonic(mnemonic))

    def test_check_mnemonic_valid(self):
        """
        Test Valid Mnemonic value
        """
        mnemonic = (
            "engine survey rich year woman keen thrive clip patrol patrol next quantum"
        )
        self.assertTrue(check_mnemonic(mnemonic))
