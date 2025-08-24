from django.test import TestCase
from django.urls import reverse


# Unit tests for forms
class TestUrls(TestCase):
    """
    Unit tests for app urls
    """

    def setUp(self):
        pass

    def test_card_url(self):
        """
        Test library card url in Library Card
        """
        url = reverse(
            "library_card:library_card",
            args=["npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"],
        )
        self.assertEqual(
            url,
            "/card/npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n/",
        )

    def tearDown(self):
        pass
