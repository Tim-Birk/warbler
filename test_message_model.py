"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError  

from models import db, Message, User, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        Likes.query.delete()
        User.query.delete()
        Message.query.delete()

        # create 2 test users to test creating messages and likes
        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        # create a test message
        m = Message(
            text="Test message. Blah Blah Blah.",
            user_id=u1.id
        )
        db.session.add(m)
        db.session.commit()

        self.test_user1 = u1
        self.test_user2 = u2
        self.message = m

        self.client = app.test_client()

    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text="This is a test message",
            user_id=self.test_user1.id
        )

        db.session.add(m)
        db.session.commit()

        self.assertIsInstance(m.id, int)

    def test_likes_model(self):
        """Does basic likes work?"""

        # add like from another user
        l = Likes(
            user_id=self.test_user2.id,
            message_id=self.message.id
        )

        db.session.add(l)
        db.session.commit()

        self.assertIsInstance(l.id, int)
        # Like should be now be in user's likes
        self.assertIn(self.message, self.test_user2.likes)
