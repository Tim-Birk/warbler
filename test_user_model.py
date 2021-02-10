"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError  

from models import db, User, Message, Follows

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        # create 2 test users to test the various methods and unique restraints
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

        self.test_user1 = u1
        self.test_user2 = u2
        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr_method(self):
        """Does the repr method work as expected?"""
        self.assertEqual(self.test_user1.__repr__(), f"<User #{self.test_user1.id}: testuser1, test1@test.com>")

    def test_is_following_method(self):
        """Does the is_following method work as expected?"""
        self.test_user1.following.append(self.test_user2)
        db.session.commit()

        # Does is_following successfully detect when user1 is following user2?
        self.assertEqual(self.test_user1.is_following(self.test_user2), True)
        # Does is_following successfully detect when user1 is not following user2?
        self.test_user1.following.remove(self.test_user2)
        db.session.commit()
        self.assertEqual(self.test_user1.is_following(self.test_user2), False)


    def test_is_followed_by_method(self):
        """Does the is_followed_by method work as expected?"""
        self.test_user1.followers.append(self.test_user2)
        db.session.commit()

        # Does is_followed_by successfully detect when user1 is followed by user2?
        self.assertEqual(self.test_user1.is_followed_by(self.test_user2), True)
        # Does is_followed_by successfully detect when user1 is not followed by user2?
        self.test_user1.followers.remove(self.test_user2)
        db.session.commit()
        self.assertEqual(self.test_user1.is_followed_by(self.test_user2), False) 

    def test_sign_up_method_valid(self):
        """Does the sign_up method work as expected given valid input and credentials?"""

        user = User.signup(
            username="user123",
            password="password123",
            email="test123@test.com",
            image_url=None
        )

        db.session.commit()
        # Does User.create successfully create a new user given valid credentials?
        self.assertIsInstance(user.id, int)
        self.assertEqual(user.username, 'user123')
        self.assertEqual(user.email, 'test123@test.com')
        self.assertEqual(user.image_url, '/static/images/default-pic.png')
        self.assertEqual(user.header_image_url, '/static/images/warbler-hero.jpg')

    def test_sign_up_method_invalid(self):
        """Does the sign_up method work as expected given invalid input/credentials?"""
        cases = [
            {'username': 'testuser3', 'password': 'password123', 'email': 'test1@test.com', 'image_url': None}, # duplicate email
            {'username': 'testuser1', 'password': 'password123', 'email': 'dogfan1@test.com', 'image_url': None}, # duplicate user name
            {'username': None, 'password': 'password123', 'email': 'dogfan1@test.com', 'image_url': None}, # null user name
            {'username': 'testuser11234', 'password': 'password123', 'email': None, 'image_url': None} # null email
        ]

        # Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?    
        for case in cases:
            user = User.signup(
                username=case['username'],
                password=case['password'],
                email=case['email'],
                image_url=case['image_url']
            )
            
            failed = False
            try:
                db.session.commit()
            except IntegrityError as ie:
                failed = True
                self.assertIsInstance(ie, IntegrityError)
                db.session.rollback()
            
            self.assertEqual(failed, True)
                           
    def test_authenticate_valid(self):
        """Does the User.authenticate method work as expected given valid username and password?"""

        user = User.signup(
            username="user123",
            password="password123",
            email="test123@test.com",
            image_url=None
        )

        db.session.commit()

        good_user = User.authenticate('user123', password="password123")
        # Does User.authenticate successfully return a user when given a valid username and password?
        self.assertIsInstance(good_user.id, int)
        self.assertEqual(good_user.username, 'user123')
        self.assertEqual(good_user.email, 'test123@test.com')
        self.assertEqual(good_user.image_url, '/static/images/default-pic.png')
        self.assertEqual(good_user.header_image_url, '/static/images/warbler-hero.jpg')

        # Does User.authenticate fail to return a user when the username is invalid?
        bad_user = User.authenticate('user123456789', password="password123")
        self.assertEqual(bad_user, False)
        # Does User.authenticate fail to return a user when the password is invalid? 
        bad_user = User.authenticate('user123', password="wrongPassword")
        self.assertEqual(bad_user, False)
            
         
        



       