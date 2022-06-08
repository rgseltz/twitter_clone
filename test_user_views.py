from cgi import test
from app import app, session
import os
from unittest import TestCase
from models import User, Message, Follows, db
os.environ['DATABASE_URI'] = 'postgresql:///warbler_test'

db.drop_all()
db.create_all()


class TestUserViews(TestCase):
    def setUp(self):
        """Create a user"""

        User.query.delete()

        test_user = User.signup(
            'testName', 'test@email.com', 'testPAssword', None)
        self.test_user = test_user
        self.test_user_id = 27
        self.test_user.id = self.test_user.id
        user2 = User.signup('user1', 'user1@testEmail.com', 'lala', None)
        self.user2 = user2
        self.user2_id = 58
        self.user2.id = self.user2_id
        db.session.add(test_user)
        db.session.add(user2)
        db.session.commit()
        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_root_route(self):
        with app.test_client() as client:
            resp = client.get("/")
            html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<!DOCTYPE html>', html)

    def test_is_logged_in(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session['CURR_USER_KEY'] = self.test_user_id
            resp = client.get("/login")

            self.assertEqual(resp.status_code, 200)
            self.assertTrue(session['CURR_USER_KEY'], True)
            self.assertEqual(session['CURR_USER_KEY'], self.test_user_id)
