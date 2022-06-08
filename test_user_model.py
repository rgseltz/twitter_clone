"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

from app import app
from plistlib import UID

import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User.signup('user1', 'user1@email.com', 'password', None)
        u1id = 1
        u1.id = u1id

        u2 = User.signup('user2', 'user2@email.com', 'password2', None)
        u2id = 2
        u2.id = u2id

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        self.u1 = u1
        self.u1id = u1id

        self.u2 = u2
        self.u2id = u2id

        self.client = app.test_client()

    # def test_user_model(self):
    #     """Does basic model work?"""

        self.u1 = u1
        self.u2 = u2

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)

    def test_user_follows(self):
        self.u1.following.append(self.u2)

        self.assertEqual(len(self.u1.following), 1)
        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(self.u1.following[0], self.u2)

        self.u2.following.append(self.u1)
        self.assertEqual(self.u2.following[0], self.u1)

    def test_user_is_following(self):
        self.u1.following.append(self.u2)

        self.assertEqual(self.u1.is_following(self.u2), True)
        self.assertEqual(self.u1.is_followed_by(self.u2), False)
        self.assertEqual(self.u2.is_followed_by(self.u1), True)

        self.u2.following.append(self.u1)
        self.assertEqual(self.u2.is_following(self.u1), True)
        self.assertEqual(self.u1.is_following(self.u2), True)

    def test_new_user(self):
        u_test = User.signup(
            'usertest1', 'usertest1@test.com', 'testuser1password', None)
        id = 10
        u_test.id = id
        db.session.add(u_test)
        db.session.commit()
        u_test = User.query.get(u_test.id)

        self.assertEqual(u_test.username, 'usertest1')
        self.assertEqual(self.u2.username, 'user2')
        self.assertEqual(u_test.email, 'usertest1@test.com')
