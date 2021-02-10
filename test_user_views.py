"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes

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


class UserViewTestCase(TestCase):
    """Test views for user."""

    def setUp(self):
        """Create test client, add sample data."""

        Likes.query.delete()
        Message.query.delete()
        User.query.delete()
        
        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_home_logged_in(self):
        """Does the home route display correct the html if the user is logged in"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = self.client.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<ul class="list-group" id="messages">', html)

    def test_home_logged_out(self):
        """Does the home route display correct the html if the user is logged in"""

        with self.client as c:
            resp = self.client.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<h1>What's Happening?</h1>", html)

    def test_display_sign_up_form(self):
        """Does the add sign_up route display correct the html"""

        with self.client as c:

            resp = self.client.get("/signup")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2 class="join-message">Join Warbler today.</h2>', html)

    def test_add_user(self):
        """Can user add a new user?"""
        with self.client as c:
            u = {"username": "testuser123",
                 "email": "test123@test.com",
                 "password": "testuser",
                 "image_url": None}
            resp = c.post("/signup", data=u, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<p>@testuser123</p>", html)

    def test_login_form(self):
        """Does the add login route display correct the html"""

        with self.client as c:

            resp = self.client.get("/login")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2 class="join-message">Welcome back.</h2>', html)

    def test_login_user(self):
        """Can user login?"""
        with self.client as c:
            u = {"username": "testuser",
                 "password": "testuser"}
            resp = c.post("/login", data=u, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<p>@testuser</p>", html)

    def test_logout(self):
        """Can user logout?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.get("/logout", follow_redirects=True)
            html = resp.get_data(as_text=True)

            # Does the user get redirected to the login page after logging out?
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2 class="join-message">Welcome back.</h2>', html)
            
    def test_users_display_page(self):
        """Does the route display correct the html"""

        with self.client as c:

            resp = self.client.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="card user-card">', html)

    def test_single_user_display_page(self):
        """Does the route display correct the html"""

        with self.client as c:
            #request profile for testuser
            resp = self.client.get(f"/users/{self.testuser.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            # test alt text of hero image for user
            self.assertIn(f'alt="Image for {self.testuser.username}"', html)

    def test_user_following_page(self):
        """Does the route display correct the html 
        with the correct users that the user follows?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            # Make a user to follow testuser
            u = User(
                email="doglover@test.com",
                username="doglover",
                password="HASHED_PASSWORD"
            )

            db.session.add(u)
            db.session.commit()

            # make the new user follow the testuser
            u.following.append(self.testuser)
            db.session.commit()

            #request following for new user
            resp = self.client.get(f"/users/{u.id}/following")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            # make sure username for testuser appears in p element for user card that the new user is following
            self.assertIn(f'<p>@{self.testuser.username}</p>', html)

    def test_user_followers_page(self):
        """Does the route display correct the html 
        with the correct users that follow the user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            # Make a user for testuser to follow
            u = User(
                email="doglover@test.com",
                username="doglover",
                password="HASHED_PASSWORD"
            )

            db.session.add(u)
            db.session.commit()

            # Make the testuser a follower of the new user
            u.followers.append(self.testuser)
            db.session.commit()

            #request followers for new user
            resp = self.client.get(f"/users/{u.id}/followers")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            # make sure username for testuser appears in p element for user card that follows new user
            self.assertIn(f'<p>@{self.testuser.username}</p>', html)

    def test_add_follow(self):
        """Can user add a new follow?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            # create a user for the test user to follow
            u = User(
                email="doglover@test.com",
                username="doglover",
                password="HASHED_PASSWORD"
            )

            db.session.add(u)
            db.session.commit()
            
            resp = c.post(f"/users/follow/{u.id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<p>@doglover</p>", html)

    def test_remove_follow(self):
        """Can user remove an existing follow?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            # create a user for the test user to follow
            u = User(
                email="doglover@test.com",
                username="doglover",
                password="HASHED_PASSWORD"
            )

            db.session.add(u)
            db.session.commit()
            
            # make test user follow new user
            test_user = User.query.get(self.testuser.id)
            test_user.following.append(u)
            db.session.commit()

            # make sure new user is in test user's following
            self.assertIn(u, test_user.following)

            # user remove route to remove new user from following
            resp = c.post(f"/users/stop-following/{u.id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            # make sure new user is no longer in test user's following
            test_user = User.query.get(self.testuser.id)
            self.assertNotIn(u, test_user.following)

    def test_display_user_profile(self):
        """Does the user profile route display correct the html"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = self.client.get(f"/users/{self.testuser.id}/profile")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2 class="join-message">Edit Your Profile.</h2>', html)

    def test_update_user(self):
        """Can user update their profile info?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            u = {"username": "testuser123",
                 "email": "test123@test.com",
                 "password": "testuser",
                 "image_url": "https://scontent-lga3-2.xx.fbcdn.net/v/t1.0-9/56649400_10103839445921552_8360508541538140160_o.jpg?_nc_cat=108&ccb=3&_nc_sid=09cbfe&_nc_ohc=bFnauW7KR94AX8UeOwk&_nc_ht=scontent-lga3-2.xx&oh=452f0cb3842132ad293790909ddbd32e&oe=6046FA1E",
                 "header_image_url": "http://parksadventure.com/wp-content/uploads/2017/10/header-image-1-2.png",
                 "bio": "This is a newly added bio from the update",
                 "location": "Newly Added Location"}

            # update test user using the update route
            resp = c.post(f"/users/{self.testuser.id}/profile", data=u, follow_redirects=True)
            html = resp.get_data(as_text=True)

            # check response and redirect to correct html for user profile
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h4 id="sidebar-username">@testuser123</h4>', html)

            # check testuser's info has been updated correctly
            test_user = User.query.get(self.testuser.id)
            self.assertEqual(test_user.username,"testuser123")
            self.assertEqual(test_user.email,"test123@test.com")
            self.assertEqual(test_user.image_url,"https://scontent-lga3-2.xx.fbcdn.net/v/t1.0-9/56649400_10103839445921552_8360508541538140160_o.jpg?_nc_cat=108&ccb=3&_nc_sid=09cbfe&_nc_ohc=bFnauW7KR94AX8UeOwk&_nc_ht=scontent-lga3-2.xx&oh=452f0cb3842132ad293790909ddbd32e&oe=6046FA1E")
            self.assertEqual(test_user.header_image_url,"http://parksadventure.com/wp-content/uploads/2017/10/header-image-1-2.png")
            self.assertEqual(test_user.bio,"This is a newly added bio from the update")
            self.assertEqual(test_user.location,"Newly Added Location")

    def test_delete_user(self):
        """Can user delete their account?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post(f"/users/{self.testuser.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            
            # check redirect to signup
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2 class="join-message">Join Warbler today.</h2>', html)

            # check test user is deleted
            test_user = User.query.get(self.testuser.id)
            self.assertEqual(test_user, None)

    def test_toggle_like(self):
        """Can user add and remove likes?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            u = User(
                email="doglover@test.com",
                username="doglover",
                password="HASHED_PASSWORD"
            )

            db.session.add(u)
            db.session.commit()
            
            # make a test message from new user for testuser to like
            m = Message(
                text="Test message. Blah Blah Blah.",
                user_id=u.id
            )
            db.session.add(m)
            db.session.commit()
            # save message.id to variable for after request is made
            msg_id = m.id

            # use like toggle route to add like for test user to new message
            resp = c.post(f"/users/add_like/{msg_id}", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)

            # make sure message is in testuser's likes
            msg = Message.query.get(msg_id)
            test_user = User.query.get(self.testuser.id)
            self.assertIn(msg, test_user.likes)

            # use like toggle route to remove like for test user 
            resp = c.post(f"/users/add_like/{msg_id}", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)

            # make sure message is no longer in testuser's likes
            msg = Message.query.get(msg_id)
            test_user = User.query.get(self.testuser.id)
            self.assertNotIn(msg, test_user.likes)

    def test_user_like_loggedin(self):
        """Does the user likes display all of the liked messages for the user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            # create a user for the test user to follow
            u = User(
                email="doglover@test.com",
                username="doglover",
                password="HASHED_PASSWORD"
            )

            db.session.add(u)
            db.session.commit()
            
            # make a test message from new user for testuser to like
            m = Message(
                text="Test message. Blah Blah Blah.",
                user_id=u.id
            )
            db.session.add(m)
            db.session.commit()
            
            test_user = User.query.get(self.testuser.id)
            test_user.likes.append(m)
            db.session.commit()
            
            resp = self.client.get(f"/users/{self.testuser.id}/likes")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<a href="/messages/{m.id}" class="message-link"', html)

    def test_user_like_loggedout(self):
        """Is the user prohibited from seeing user likes if they're logged out?"""
        with self.client as c:
            # create a user for the test user to follow
            u = User(
                email="doglover@test.com",
                username="doglover",
                password="HASHED_PASSWORD"
            )

            db.session.add(u)
            db.session.commit()
            
            # make a test message from new user for testuser to like
            m = Message(
                text="Test message. Blah Blah Blah.",
                user_id=u.id
            )
            db.session.add(m)
            db.session.commit()
            
            test_user = User.query.get(self.testuser.id)
            test_user.likes.append(m)
            db.session.commit()
            
            resp = self.client.get(f"/users/{self.testuser.id}/likes", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<div class="alert alert-danger">Access unauthorized.</div>', html)
