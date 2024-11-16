from django.test import TestCase
from utils.Login import check_npub, check_nsec, check_npub_of_nsec, check_mnemonic

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
        npub = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
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
        nsec = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        self.assertTrue(check_nsec(nsec))
    
    def test_check_npub_of_nsec(self):
        """
        Test Invalid NSEC value
        """
        nsec = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        npub = "npub1039j8zfxafe5xtx5qhmjf02rv7upgwgx54kd35e5qehj36egkjuqx9f704"
        self.assertFalse(check_npub_of_nsec(npub, nsec))
    
    def test_check_npub_of_nsec_valid(self):
        """
        Test Valid NSEC value
        """
        nsec = "nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm"
        npub = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"
        self.assertTrue(check_npub_of_nsec(npub, nsec))

    def test_check_mnemonic_invalid(self):
        """
        Test Invalid Mnemonic value
        """
        mnemonic = "apple banana cherry date egg fig grape honey ice juice kiwi lemon"
        self.assertFalse(check_mnemonic(mnemonic))
    
    def test_check_mnemonic_valid(self):
        """
        Test Valid Mnemonic value
        """
        mnemonic = "engine survey rich year woman keen thrive clip patrol patrol next quantum"
        self.assertTrue(check_mnemonic(mnemonic))