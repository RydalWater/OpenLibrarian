from django.test import TestCase
from utils.Network import get_event_relays
import os
import ast
import json


class TestNetwork(TestCase):
    """Test the Network module"""

    def setUp(self):
        """Setup the test"""
        pass

    def test_get_event_relays(self):
        """Test get_event_relays"""
        relays_dict = {"relay1": "WRITE", "relay2": "READ"}
        relays_list = ["relay1", "relay2"]
        self.assertEqual(
            get_event_relays(relays_dict=relays_dict), json.dumps(["relay1"])
        )
        self.assertEqual(
            get_event_relays(relays_list=relays_list), json.dumps(["relay1", "relay2"])
        )

        # Get relays from env
        relays_list = ast.literal_eval(os.getenv("DEFAULT_RELAYS"))
        self.assertEqual(get_event_relays(), json.dumps(relays_list))

    def tearDown(self):
        """Tear down the test"""
        pass
