"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message_loggedout(self):
        """Can user add a message if they're logged out?"""

        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<div class="alert alert-danger">Access unauthorized.</div>', html)

    def test_add_message_loggedin(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_add_user_redirect(self):
        """Does adding a new message redirect to correct html?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<ul class="list-group" id="messages">', html)

    def test_display_add_message_form(self):
        """Does the add message route display correct the html"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = self.client.get("/messages/new")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<button class="btn btn-outline-success btn-block">Add my message!</button>', html)

    def test_show_message(self):
        """Does the show message route display correct the html"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            m = Message(
                text="Test message. Blah Blah Blah.",
                user_id=self.testuser.id
            )
            db.session.add(m)
            db.session.commit()
            
            resp = self.client.get(f"/messages/{m.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p class="single-message">Test message. Blah Blah Blah.</p>', html)

    def test_delete_message_logged_in(self):
        """Can use delete a message?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test
            m = Message(
                text="Test message. Blah Blah Blah.",
                user_id=self.testuser.id
            )
            db.session.add(m)
            db.session.commit()

            resp = c.post(f"/messages/{m.id}/delete")

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

    def test_delete_message_logged_out(self):
        """Can user delete a message if they're logged out?"""
        with self.client as c:
            m = Message(
                text="Test message. Blah Blah Blah.",
                user_id=self.testuser.id
            )
            db.session.add(m)
            db.session.commit()

            resp = c.post(f"/messages/{m.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<div class="alert alert-danger">Access unauthorized.</div>', html)

