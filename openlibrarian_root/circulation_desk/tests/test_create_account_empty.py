import json
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock

TC_NPUB = "npub1dpzan5jvyp0kl0sykx29397f7cnazgwa3mtkfyt8d9gga7htm9xsdsk85n"

class TestCreateAccountEmptyView(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('circulation_desk:create_account_empty')

    def test_get_request(self):
        """
        Test that a GET request returns a redirect
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_post_request_with_invalid_json(self):
        """
        Test that a POST request with invalid JSON returns a JSON response
        """
        response = self.client.post(self.url, 'invalid json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'result': 'Failed to create account'})

    def test_post_request_with_missing_npub(self):
        """
        Test that a POST request with missing npub returns a JSON response
        """
        data = json.dumps({'hasNsec': 'Y'})
        with self.assertRaises(Exception) as e:
            response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(str(e.exception), "No npub provided or invalid npub.")
        

    def test_post_request_with_missing_nsec(self):
        """
        Test that a POST request with missing nsec returns a JSON response
        """
        data = json.dumps({'npubValue': TC_NPUB})
        response = self.client.post(self.url, data, content_type='application/json')
        session = self.client.session
        self.assertEqual(response.status_code, 200)
        self.assertEqual(session['npub'], TC_NPUB)
        self.assertEqual(session["progress"], {})
        self.assertEqual(session["reviews"], {})
        self.assertEqual(session["interests"], [])
        self.assertEqual(session["libraries"], [{'s': 'TRS', 'i': 'a0c752fef8feda7af2da45c612615191ed5f844b', 't': 'To Read (S)', 'd': 'Books on the shelf ready to read', 'c': 'Books & Literature (OpenLibrarian)', 'b': []}, {'s': 'TRW', 'i': 'a441ab2ab6b6b56d69b6a8a820e15367d94282b9', 't': 'To Read (W)', 'd': "Books I want to read but don't own yet", 'c': 'Books & Literature (OpenLibrarian)', 'b': []}, {'s': 'CR', 'i': '4e5ae5e37e7d6063daa4ffadf13a01a90d39eafe', 't': 'Currently Reading', 'd': 'Books I am currently reading', 'c': 'Books & Literature (OpenLibrarian)', 'b': []}, {'s': 'HR', 'i': 'b7479212546095f547a5adbf46cdcc9bf2368663', 't': 'Have Read', 'd': 'Books I have finished reading', 'c': 'Books & Literature (OpenLibrarian)', 'b': []}])
        relays = ['wss://relay.damus.io', 'wss://relay.primal.net', 'wss://nos.lol', 'wss://nostr.mom']
        for relay in relays:
            self.assertIn(relay, session["relays"])
        json_response = response.json()
        self.assertIn(":10002", json_response["raw_events"])
        for relay in relays:
            self.assertIn(relay, json_response["raw_events"])
