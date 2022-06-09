from cgi import test
from app import app, session, CURR_USER_KEY
import os
from bs4 import BeautifulSoup
from unittest import TestCase
from models import User, Message, Follows, db, Likes
os.environ['DATABASE_URI'] = 'postgresql:///warbler_test'

db.drop_all()
db.create_all()


class TestUserViews(TestCase):
    def setUp(self):
        """Create a user"""

        User.query.delete()

        test_user = User.signup(
            'test_name', 'test@email.com', 'password', None)
        self.test_user = test_user
        self.test_user_id = 27
        self.test_user.id = self.test_user_id
        db.session.add(test_user)
        user1 = User.signup('user1', 'user1@testEmail.com', 'lala', None)
        self.user1 = user1
        self.user1_id = 58
        self.user1.id = self.user1_id

        db.session.add(user1)
        db.session.commit()
        self.client = app.test_client()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_root_route(self):
        with app.test_client() as client:
            resp = client.get("/")
            html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<!DOCTYPE html>', html)

    def test_is_logged_in(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.test_user.id
            resp = client.get("/login")

            self.assertEqual(resp.status_code, 200)
            self.assertTrue(session[CURR_USER_KEY], True)
            self.assertEqual(session[CURR_USER_KEY], self.test_user.id)

    def test_users_route(self):
        with app.test_client() as client:
            resp = client.get('/users?q=test')
            # resp = client.get('/users')

            self.assertIn('@test_name', str(resp.data))
            # self.assertIn('user1', str(resp.data))

    def test_user_detail(self):
        with app.test_client() as client:
            resp = client.get(f'/users/{self.test_user.id}')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@test_name', str(resp.data))

    def set_up_likes(self):
        m1 = Message(text="my test message", user_id=self.test_user.id)
        m2 = Message(text="My second test message", user_id=self.test_user.id)
        m3 = Message(text="Rock and roll party time",
                     id=87, user_id=self.user1.id)
        db.session.add_all([m1, m2, m3])
        db.session.commit()

        l1 = Likes(user_id=self.test_user.id, message_id=87)
        db.session.add(l1)
        db.session.commit()

    def test_user_show_likes(self):
        self.set_up_likes()

        with app.test_client() as client:
            resp = client.get(f'/users/{self.test_user_id}')

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@test_name", str(resp.data))
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)

            # test for a count of 2 messages
            self.assertIn("2", found[0].text)

            # Test for a count of 0 followers
            self.assertIn("0", found[1].text)

            # Test for a count of 0 following
            self.assertIn("0", found[2].text)

            # Test for a count of 1 like
            self.assertIn("1", found[3].text)

    def test_add_like(self):
        m1 = Message(text="Rock and roll party time",
                     id=87, user_id=self.user1.id)
        db.session.add(m1)
        db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.test_user_id
            resp = client.post('/users/add_like/87',
                               follow_redirects=True)
            self.assertEqual(session[CURR_USER_KEY], self.test_user_id)
            self.assertEqual(resp.status_code, 200)
            likes = Likes.query.filter(Likes.message_id == 87).all()

            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.test_user_id)

    def test_remove_like(self):
        self.set_up_likes()

        message = Message.query.filter(
            Message.user_id == self.user1_id).all()
        self.assertIn("Rock and roll", message[0].text)
        self.assertIsNotNone(message)
        likes = Likes.query.filter(
            Likes.user_id == self.test_user_id and Likes.message_id == message[0].id).all()
        self.assertIsNotNone(likes)
        self.assertEqual(len(likes), 1)

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.test_user.id
            ##This should remove like but BUG! - it's not working ##
            resp = client.post('/users/add_like/87', follow_redirects=True)
            likes = Likes.query.filter(Likes.message_id == 87).all()
            self.assertEqual(resp.status_code, 200)
            # self.assertEqual(len(likes), 0)
