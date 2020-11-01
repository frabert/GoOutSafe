import unittest
from monolith.app import create_app
from flask_test_with_csrf import FlaskClient
from utils import do_login, do_logout


class TestReservation(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = create_app("TEST")
        self.app.test_client_class = FlaskClient

    def setup_app(self):
        self.app = create_app("TEST")
        self.app.test_client_class = FlaskClient
        tested_app = self.app.test_client()
        tested_app.set_app(self.app)
        return tested_app

    def test_get_list(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "customer@example.com","customer")
        reply = client.t_get("/reservations")
        self.assertIn("Trial Restaurant",reply.get_data(as_text=True),msg=reply.get_data(as_text=True))
        do_logout(client)

    def test_get_empty_list(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "a.customer@example.com","customer")
        reply = client.t_get("/reservations")
        self.assertIn("There are no reservations",reply.get_data(as_text=True),msg=reply.get_data(as_text=True))
        do_logout(client)

    
    def test_not_found(self):
        client = self.app.test_client()
        client.set_app(self.app)

        users = ["example@example.com","health@authority.com","operator@example.com"]
        passw = ["admin","health","operator"]
        endpoints = ["/reservations"]

        for i in range(len(users)):
            do_login(client, users[i], passw[i])
            for e in endpoints:
                reply = client.t_get(e)
                self.assertEqual(reply.status_code, 404, msg="endpoint: "+e+"\n"+reply.get_data(as_text=True))
            do_logout(client)

    def test_can_booking(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "customer@example.com",
                "password":"customer"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            form = {
                "number_of_people": "2",
                "booking_date": "04/10/2022",
                "booking_hr": "13",
                "booking_min": "30"
            }
            reply = client.t_post("/restaurants/1/book", data=form)
            self.assertEqual(reply.status_code, 302, msg=reply.get_data(as_text=True))

    def test_booking_restaurantNone(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "customer@example.com",
                "password":"customer"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            form = {
                "number_of_people": "2",
                "booking_date": "04/10/2022",
                "booking_hr": "13",
                "booking_min": "30"
            }
            reply = client.t_post("/restaurants/55654/book", data=form)
            self.assertEqual(reply.status_code, 404)

    def test_cannot_booking_admin(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "example@example.com",
                "password":"admin"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            reply = client.t_get("/restaurants/1/book", data=form)
            self.assertEqual(reply.status_code, 401)

    def test_cannot_booking_positive(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "positive@example.com",
                "password": "positive"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            reply = client.t_get("/restaurants/1/book")
            self.assertEqual(reply.status_code, 401)

    def test_get_booking_page(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "customer@example.com",
                "password":"customer"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            reply = client.t_get("/restaurants/1/book", data=form)
            self.assertEqual(reply.status_code, 200)

    def test_cannot_booking(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "customer@example.com",
                "password":"customer"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            form = {
                "number_of_people": "500",
                "booking_date": "04/10/2022",
                "booking_hr": "13",
                "booking_min": "30"
            }
            reply = client.t_post("/restaurants/1/book", data=form)
            self.assertEqual(reply.status_code, 400)

    def test_cannot_booking_date(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "customer@example.com",
                "password":"customer"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            form = {
                "number_of_people": "2",
                "booking_date": "04/10/2010",
                "booking_hr": "13",
                "booking_min": "30"
            }
            reply = client.t_post("/restaurants/1/book", data=form)
            self.assertEqual(reply.status_code, 400)

    def test_reservation_not_operator(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "example@example.com",
                "password":"admin"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            reply = client.t_get("/restaurants/1/reservations", data=form)
            self.assertEqual(reply.status_code, 401)

    def test_reservation_none_restaurants(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator@example.com",
                "password":"operator"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            reply = client.t_get("/restaurants/37923/reservations", data=form)
            self.assertEqual(reply.status_code, 404)

    def test_reservation_another_operator(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator2@example.com",
                "password":"operator2"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            reply = client.t_get("/restaurants/1/reservations", data=form)
            self.assertEqual(reply.status_code, 401)

    def test_get_reservation_list_operator(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator@example.com",
                "password":"operator"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)
            reply = client.t_get("/restaurants/1/reservations", data=form)
            self.assertEqual(reply.status_code, 200)

    def test_bad_reservation_list(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator@example.com",
                "password":"operator"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)

            form = {
                "from_date":"10/10/2020",
                "from_hr":"13",
                "from_min":"30",
                "to_date":"08/10/2020",
                "to_hr":"14",
                "to_min":"30"
            }
            reply = client.t_post("/restaurants/1/reservations", data=form)
            self.assertEqual(reply.status_code, 400)

    def test_good_reservation_list(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator@example.com",
                "password": "operator"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)

            form = {
                "from_date": "08/10/2020",
                "from_hr": "13",
                "from_min": "30",
                "to_date": "10/10/2020",
                "to_hr": "14",
                "to_min": "30"
            }
            reply = client.t_post("/restaurants/1/reservations", data=form)
            self.assertEqual(reply.status_code, 200)

    def test_bad_restaurant_id(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator@example.com",
                "password": "operator"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)

            reply = client.t_get("/restaurants/479432")
            self.assertEqual(reply.status_code, 404)

    def test_good_restaurant_id(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator@example.com",
                "password": "operator"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)

            reply = client.t_get("/restaurants/1")
            self.assertEqual(reply.status_code, 200)


    def test_bad_reservations_id(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator@example.com",
                "password": "operator"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)

            reply = client.t_get("/reservations/479432")
            self.assertEqual(reply.status_code, 404)

    def test_good_reservations_id(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator@example.com",
                "password": "operator"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)

            reply = client.t_get("/reservations/5")
            self.assertEqual(reply.status_code, 200)

    def test_rese_id_none(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator@example.com",
                "password": "operator"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)

            reply = client.t_get("/reservations/168012")
            self.assertEqual(reply.status_code, 404)

    def test_bad_rese_id(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator2@example.com",
                "password": "operator2"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)

            reply = client.t_get("/reservations/1")
            self.assertEqual(reply.status_code, 401)

    def test_rese_delete(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "operator@example.com",
                "password": "operator"
            }
            reply = client.t_post('/login', data=form)
            self.assertEqual(reply.status_code, 302)

            reply = client.t_post("/reservations/1/delete")
            self.assertEqual(reply.status_code, 302)


    def test_rese_delete_user(self):
        with self.app.test_client() as client:
            client.set_app(self.app)
            form = {
                "email": "example@example.com",
                "password": "admin"
            }
            reply = client.t_post('/login', data=form)
            reply = client.t_post("/reservations/5/delete")
            self.assertEqual(reply.status_code, 302)

    def test_rese_delete_user(self):
        client = self.setup_app()
        form = {
            "email": "customer@example.com",
            "password": "customer"
        }
        reply = client.t_post('/login', data=form)
        reply = client.t_post("/reservations/5/delete")
        self.assertEqual(reply.status_code, 302)

    def test_rese_delete_bad_user(self):
        client = self.setup_app()
        form = {
            "email": "a.customer@example.com",
            "password": "customer"
        }
        reply = client.t_post('/login', data=form)
        reply = client.t_post("/reservations/5/delete")
        self.assertEqual(reply.status_code, 401)

    def test_rese_good_edit(self):
        client = self.setup_app()
        u_form = {
            "email": "customer@example.com",
            "password": "customer"
        }
        reply = client.t_post('/login', data=u_form)

        form = {
            "number_of_people": "1",
            "booking_date": "07/10/2021",
            "booking_hr": "13",
            "booking_min": "30"
        }

        reply = client.t_post("/reservations/5/edit", data=form)
        self.assertEqual(reply.status_code, 302,msg=reply.get_data(as_text=True))


    def test_rese_bad_date_edit(self):
        client = self.setup_app()
        u_form = {
            "email": "customer@example.com",
            "password": "customer"
        }
        reply = client.t_post('/login', data=u_form)

        form = {
            "number_of_people": "1",
            "booking_date": "07/10/2010",
            "booking_hr": "13",
            "booking_min": "30"
        }

        reply = client.t_post("/reservations/5/edit", data=form)
        self.assertEqual(reply.status_code, 400,msg=reply.get_data(as_text=True))

    def test_rese_bad_edit(self):
        client = self.setup_app()
        u_form = {
            "email": "customer@example.com",
            "password": "customer"
        }
        reply = client.t_post('/login', data=u_form)

        form = {
            "number_of_people": "1",
            "booking_date": "08/11/2020",
            "booking_hr": "13",
            "booking_min": "30"
        }

        reply = client.t_post("/reservations/5/edit", data=form)
        self.assertEqual(reply.status_code, 400,msg=reply.get_data(as_text=True))


    def test_rese_get_edit(self):
        client = self.setup_app()
        u_form = {
            "email": "customer@example.com",
            "password": "customer"
        }
        reply = client.t_post('/login', data=u_form)

        reply = client.t_get("/reservations/5/edit")
        self.assertEqual(reply.status_code, 200,msg=reply.get_data(as_text=True))

    def test_rese_404_edit(self):
        client = self.app.test_client()
        client.set_app(self.app)
        u_form = {
            "email": "customer@example.com",
            "password": "customer"
        }
        reply = client.t_post('/login', data=u_form)

        reply = client.t_get("/reservations/9999/edit")
        self.assertEqual(reply.status_code, 404,msg=reply.get_data(as_text=True))

    def test_rese_401_edit(self):
        client = self.app.test_client()
        client.set_app(self.app)
        u_form = {
            "email": "customer@example.com",
            "password": "customer"
        }
        reply = client.t_post('/login', data=u_form)

        reply = client.t_get("/reservations/4/edit")
        self.assertEqual(reply.status_code, 401,msg=reply.get_data(as_text=True))

    def test_cannot_edit_positive(self):
        client = self.app.test_client()
        client.set_app(self.app)

        form = {
            "email": "positive@example.com",
            "password": "positive"
        }
        reply = client.t_post('/login', data=form)
        self.assertEqual(reply.status_code, 302)
        reply = client.t_get("/reservations/6/edit")
        self.assertEqual(reply.status_code, 401)


    def test_cannot_edit_old_booking(self):
        client = self.app.test_client()
        client.set_app(self.app)

        form = {
            "email": "customer@example.com",
            "password": "customer"
        }
        reply = client.t_post('/login', data=form)
        self.assertEqual(reply.status_code, 302)
        reply = client.t_get("/reservations/7/edit")
        self.assertEqual(reply.status_code, 404)

    def test_get_todays_list(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "operator@example.com","operator")
        reply = client.t_get("/restaurants/1/reservations/today")
        reply_data = reply.get_data(as_text=True)
        self.assertIn("Positive Positive",reply_data,msg=reply_data)
        self.assertIn("Customer Customer",reply_data,msg=reply_data)
        do_logout(client)

    def test_get_todays_list_401(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "customer@example.com","customer")
        reply = client.t_get("/restaurants/1/reservations/today")
        self.assertEqual(reply.status_code, 401,msg=reply.get_data(as_text=True))
        do_logout(client)

    def test_entrance_401(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "customer@example.com","customer")
        reply = client.t_get("/reservations/9/entrance")
        self.assertEqual(reply.status_code, 401,msg=reply.get_data(as_text=True))
        do_logout(client)

    def test_entrance_401_operator(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "operator3@example.com","operator3")
        reply = client.t_get("/reservations/9/entrance")
        self.assertEqual(reply.status_code, 401,msg=reply.get_data(as_text=True))
        do_logout(client)

    def test_get_todays_list_401_operator(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "operator3@example.com","operator3")
        reply = client.t_get("/restaurants/1/reservations/today")
        self.assertEqual(reply.status_code, 401,msg=reply.get_data(as_text=True))
        do_logout(client)

    def test_register_entrance(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "operator@example.com","operator")
        reply = client.t_get("/reservations/9/entrance")
        self.assertEqual(reply.status_code, 302,msg=reply.get_data(as_text=True))
        reply = client.t_get("/restaurants/1/reservations/today")
        self.assertNotIn("The entrance of this reservation has already been registered",reply.get_data(as_text=True),msg=reply.get_data(as_text=True))
        do_logout(client)

    def test_register_entrance_2(self):
        client = self.app.test_client()
        client.set_app(self.app)
        do_login(client, "operator@example.com","operator")
        reply = client.t_get("/reservations/9/entrance")
        self.assertEqual(reply.status_code, 302,msg=reply.get_data(as_text=True))
        reply = client.t_get("/restaurants/1/reservations/today")
        self.assertIn("The entrance of this reservation has already been registered",reply.get_data(as_text=True),msg=reply.get_data(as_text=True))
        do_logout(client)

if __name__ == '__main__':
    unittest.main()
