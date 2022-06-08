from app import app
import os
from unittest import TestCase
from models import User, Message, Follows, db
os.environ['DATABASE_URI'] = 'postgresql:///warbler_test'

db.create_all()


class MessageModelTestCase(TestCase):
    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User.signup('user1', 'user1@email.com', 'password', None)
        u1id = 1
        u1.id = u1id

        u2 = User.signup('user2', 'user2@email.com', 'password2', None)
        u2id2 = 2

        db.session.add(u1)
        db.session.add(u2)
        # db.session.add(m1)
        db.session.commit()

        self.u2 = u2
        self.u2.id = u2id2
        m1 = Message(text="testytest", user_id=1)
        m2 = Message(text="test2", user_id=2)
        m1id1 = 1
        m1.id = m1id1
        m2id2 = 2
        m2.id = m2id2

        db.session.add(m2)
        db.session.add(m1)
        db.session.commit()

        self.m1 = m1
        self.m1.id = m1id1
        self.m2id = m2id2

        self.assertEqual(m2.id, 2)
        self.assertEqual(m2.text, "test2")
        self.client = app.test_client()

    def test_new_message(self):
        """Testing new messages"""

        t_message = Message(text="test message", user_id=1)
        db.session.add(t_message)
        db.session.commit()

        self.assertEqual(self.m1.id, 1)
        self.assertEqual(t_message.text, 'test message')
        self.assertEqual(t_message.user_id, 1)
        self.assertFalse(t_message.user_id == 2)
        self.assertTrue(t_message.user_id == 1)
