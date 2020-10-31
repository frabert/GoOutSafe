import unittest
from monolith.app import create_app
from flask_test_with_csrf import FlaskClient
from flask import url_for
from flask_login import current_user
from utils import do_login, do_logout

class TestRestaurant(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = create_app("TEST")
        self.app.test_client_class = FlaskClient

    def test_restaurant_list(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = client.t_get("/restaurants")
        self.assertEqual(reply.status_code, 200)
        reply_data = reply.get_data(as_text = True)
        with self.app.test_request_context():
            self.assertTrue("Trial Restaurant" in reply_data)
            self.assertIn("True Italian Restaurant", reply_data)

    def test_restaurants_map(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "customer@example.com", "customer")
        reply = client.t_get("/restaurants_map")
        do_logout(client)
        self.assertEqual(reply.status_code, 200, msg=reply.get_data(as_text = True))

    def test_profile_has_name(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = client.t_get("/restaurants/1")
        self.assertEqual(reply.status_code, 200)
        reply_data = reply.get_data(as_text = True)
        with self.app.test_request_context():
            self.assertTrue("Trial Restaurant" in reply_data)

    def test_profile_has_phone(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = client.t_get("/restaurants/1")
        self.assertEqual(reply.status_code, 200)
        reply_data = reply.get_data(as_text = True)
        with self.app.test_request_context():
            self.assertTrue("555123456" in reply_data)

    def test_profile_has_opening_hours(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = client.t_get("/restaurants/1")
        self.assertEqual(reply.status_code, 200)
        reply_data = reply.get_data(as_text = True)
        with self.app.test_request_context():
            self.assertTrue("10:00" in reply_data)
            self.assertTrue("16:00" in reply_data)
            self.assertTrue("23:00" in reply_data)

    def test_profile_has_closed_days(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = client.t_get("/restaurants/1")
        self.assertEqual(reply.status_code, 200)
        reply_data = reply.get_data(as_text = True)
        with self.app.test_request_context():
            self.assertTrue("Monday" in reply_data)
            self.assertTrue("Sunday" in reply_data)
            self.assertFalse("Tuesday" in reply_data)
            self.assertFalse("Wednesday" in reply_data)
            self.assertFalse("Thursday" in reply_data)
            self.assertFalse("Friday" in reply_data)
            self.assertFalse("Saturday" in reply_data)

    def test_profile_has_cuisine_type(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = client.t_get("/restaurants/1")
        self.assertEqual(reply.status_code, 200)
        reply_data = reply.get_data(as_text = True)
        with self.app.test_request_context():
            self.assertIn("True Italian Restaurant", reply_data)

    def test_profile_has_menu(self):
        client = self.app.test_client()
        client.set_app(self.app)
        reply = client.t_get("/restaurants/1")
        self.assertEqual(reply.status_code, 200)
        reply_data = reply.get_data(as_text = True)
        with self.app.test_request_context():
            self.assertIn("Pizza", reply_data)
            self.assertIn("Pasta Bolognese", reply_data)
            self.assertIn("Breadsticks", reply_data)

    def test_can_like_once(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            reply = do_login(client, "example@example.com", "admin")
            
            reply = client.t_get("/restaurants/1/like")
            reply_data = reply.get_data(as_text = True)
            self.assertFalse("already liked" in reply_data)
            
            reply = client.t_get("/restaurants/1/like")
            reply_data = reply.get_data(as_text = True)
            self.assertIn("already liked",reply_data)
