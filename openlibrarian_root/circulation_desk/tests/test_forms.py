from django.test import TestCase
from circulation_desk.forms import npubForm, nsecForm, SeedForm

# Unit tests for forms
class TestForms(TestCase):
    """
    Unit tests for app forms
    """
    def setUp(self):
        pass
    
    def test_npub_form(self):
        """
        Test npubForm from Circulation Desk
        """
        data = {'npub': 'npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n'}
        form = npubForm(data)
        self.assertTrue(form.is_valid())

    def test_nsec_form(self):
        """
        Test nsecForm from Circulation Desk
        """
        data = {'nsec': 'nsec13m07g3kktrjjcfft27rekza8k8wkkunhp3rnv24lqe0n5yeg0k8s05xwhm'}
        form = nsecForm(data)
        self.assertTrue(form.is_valid())

    def test_seed_form(self):
        """
        Test SeedForm from Circulation Desk
        """
        data = {'word1': 'engine', 'word2': 'survey', 'word3': 'rich', 'word4': 'year', 'word5': 'woman', 'word6': 'keen', 'word7': 'thrive', 'word8': 'clip', 'word9': 'patrol', 'word10': 'patrol', 'word11': 'next', 'word12': 'quantum'}
        form = SeedForm(data)
        self.assertTrue(form.is_valid())

    def tearDown(self):
        pass
