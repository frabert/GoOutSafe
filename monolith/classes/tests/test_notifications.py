import unittest
from monolith.app import create_app
from flask_test_with_csrf import FlaskClient
from flask import url_for
from flask_login import current_user
from utils import do_login, do_logout
import datetime

class TestRestaurant(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.app = create_app("TEST")
        self.app.test_client_class = FlaskClient

    def test_notifications_need_login(self):
        client = self.app.test_client()
        client.set_app(self.app)

        reply = client.t_get("/notifications")
        self.assertEqual(reply.status_code, 401)

    def test_user_notifications(self):
        client = self.app.test_client()
        client.set_app(self.app)

        do_login(client, "alice@example.com", "alice")

        reply = client.t_get("/notifications")
        reply_data = reply.get_data(as_text=True)
        self.assertIn("t have notifications", reply_data)

        do_logout(client)
        do_login(client, "health@authority.com", "health")

        form = {
            "email":"gianni@example.com",
            "telephone":"",
            "ssn":""
            }

        reply = client.t_post("/positives/mark", form)

        do_logout(client)

        do_login(client, "alice@example.com", "alice")

        reply = client.t_get("/notifications")
        reply_data = reply.get_data(as_text=True)
        self.assertIn("You have had contact with a Covid-19 positive in the last 14 days", reply_data)

        do_logout(client)
        do_login(client, "health@authority.com", "health")

        form = {
            "email":"gianni@example.com",
            "telephone":"",
            "ssn":""
            }

        reply = client.t_post("/positives/unmark", form)

    def test_mark_as_read_needs_login(self):
        client = self.app.test_client()
        client.set_app(self.app)

        reply = client.t_get("/notifications/1/mark_as_read")
        self.assertEqual(reply.status_code, 401)

    def test_mark_as_read_invalid_id(self):
        client = self.app.test_client()
        client.set_app(self.app)

        do_login(client, "alice@example.com", "alice")

        reply = client.t_get("/notifications/9999/mark_as_read")
        self.assertEqual(reply.status_code, 404)

    def test_mark_as_read(self):
        client = self.app.test_client()
        client.set_app(self.app)

        do_login(client, "health@authority.com", "health")

        form = {
            "email":"gianni@example.com",
            "telephone":"",
            "ssn":""
            }

        reply = client.t_post("/positives/mark", form)

        do_logout(client)

        do_login(client, "alice@example.com", "alice")
        reply = client.t_get("/notifications/1/mark_as_read")
        self.assertEqual(reply.status_code, 200)

