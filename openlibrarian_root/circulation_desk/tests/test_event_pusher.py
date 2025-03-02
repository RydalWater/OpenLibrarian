import json, re, io, sys
from django.test import TestCase, Client
from django.urls import reverse
from nostr_sdk import Keys, EventBuilder
from circulation_desk.tests.test_index import TC_NPUB, TC_NSEC

dum_event = EventBuilder.text_note("This").sign_with_keys(Keys.parse(TC_NSEC)).as_json()

invalid_event = re.sub(r'"sig":"', r'"sig":"' + 'WRONG', dum_event)

class TestEventPublisher(TestCase):

    def setUp(self):
        self.client = Client()

    def test_get_request(self):
        # Test that GET requests are redirected to the index page
        response = self.client.get(reverse('circulation_desk:event_publisher'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('circulation_desk:index'))

    def test_post_request_no_nsec(self):
        # Test that POST requests with no 'nsec' in the session return a JSON response with no event message
        session = self.client.session
        session["nsec"] = None
        session.save()
        response = self.client.post(reverse('circulation_desk:event_publisher'), json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'event_message': None})

    def test_post_request_invalid_json(self):
        # Test that POST requests with invalid JSON return a JSON response with an error message
        session = self.client.session
        session['nsec'] = 'Y'
        session.save()
        response = self.client.post(reverse('circulation_desk:event_publisher'), 'invalid_json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'event_message': 'Unable to parse event.'})

    def test_post_request_valid_json_no_events(self):
        # Test that POST requests with valid JSON but no events return a JSON response with a message
        session = self.client.session
        session['nsec'] = 'Y'
        session.save()
        response = self.client.post(reverse('circulation_desk:event_publisher'), json.dumps({'events_json': '[]'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'event_message': 'No events to push.'})

    def test_post_request_valid_json_invalid_events(self):
        # Test that POST requests with valid JSON but invalid events return a JSON response with an error message
        session = self.client.session
        session['nsec'] = 'Y'
        session.save()
        response = self.client.post(reverse('circulation_desk:event_publisher'), json.dumps({'events_json': f'[{invalid_event}]'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'event_message': 'Unable to parse event.'})

    def test_post_request_valid_json_valid_events(self):
        # Test that POST requests with valid JSON and valid events return a JSON response with a success message
        session = self.client.session
        session['nsec'] = 'Y'
        session.save()
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        response = self.client.post(reverse('circulation_desk:event_publisher'), json.dumps({'events_json': json.dumps([dum_event])}), content_type='application/json')
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'event_message': 'Success: Updated.'})
        print(output.split("\n"))
        event_count = output.split("\n")[3]
        event_author = output.split("\n")[7]
        event_str = output.split("\n")[-1]
        self.assertEqual(event_count, 'TESTMODE: 1 Events found.')
        self.assertEqual(event_author, f'TESTMODE: {TC_NPUB} Author.')
        self.assertIn('"content":"This"', event_str)
        self.assertIn('"sig":"', event_str)
        self.assertIn('"created_at":', event_str)
        self.assertIn('"kind":1', event_str)
        self.assertIn(f'"pubkey":"{Keys.parse(TC_NSEC).public_key().to_hex()}"', event_str)
        self.assertIn('"id":"', event_str)
        self.assertIn('"tags":[]', event_str)