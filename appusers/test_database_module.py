"""Unit tests for appusers.database module

This module provides example Unit tests of one Application module - database.py.
Test class is based on unittest.TestCase.
Tests are prepared to be run with PyTest.
"""
import os, unittest, pytest
from flask import Flask
from appusers.database import db, User, Group


class TestDatabaseModuleClass(unittest.TestCase):
    """Test User and Group classes and operations"""

    @classmethod
    def setUpClass(cls):
        """Initialize app and create test_client"""
        cls.app = Flask(__name__, instance_relative_config=False)
        cls.app.config['TESTING'] = True
        cls.app.config['DEBUG'] = False
        cls.app.config['ENV'] = 'testing'
        # SQLAlchemy configuration for testing
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        cls.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        with cls.app.app_context():
            db.init_app(cls.app)
            db.create_all()

    def test_01_users_create(self):
        """Create test Users in database"""
        with self.app.app_context():
            johne = User(
                username='johne',
                firstname='John',
                lastname='Example',
                email='johne@example.com',
                phone='123-444-5555'
                )
            self.assertIsNotNone(johne)
            self.assertGreater(johne.userid, 0)

            self.johne_userid = johne.userid

            lindas = User(
                username='lindas',
                firstname='Linda',
                lastname='Sample',
                email='lindas@example.com',
                phone='123-444-6666'
                )
            self.assertIsNotNone(lindas)
            self.assertGreater(lindas.userid, 0)
            self.assertNotEqual(johne.userid, lindas.userid)

            lin = User(
                username='lin',
                firstname='Li',
                lastname='Nerd',
                email='lin@example.com',
                phone='123-444-7777'
                )
            self.assertIsNotNone(lin)
            self.assertGreater(lin.userid, 0)

            removeme = User(
                username='removeme',
                firstname='Remove',
                lastname='Me',
                email='removeme@example.com',
                phone='123-444-8888'
                )
            self.assertIsNotNone(removeme)
            self.assertGreater(removeme.userid, 0)

    def test_02_user_get_list_empty_filters(self):
        """Test User.get_list() method with empty filters dictionary"""
        with self.app.app_context():
            filters = {}
            users = User.get_list(filters)
            self.assertEqual(len(users), 4)
            self.assertIsInstance(users[0], User)

    def test_03_user_get_list_by_username(self):
        """Test User.get_list() method with username=johne"""
        with self.app.app_context():
            filters = {'username': 'johne'}
            users = User.get_list(filters)
            self.assertEqual(len(users), 1)
            self.assertEqual(users[0].username, 'johne')

    def test_04_user_get_list_by_firstname_lastname(self):
        """Test User.get_list() method with firstname and lastname"""
        with self.app.app_context():
            filters = {'firstname': 'Linda', 'lastname': 'Sample'}
            users = User.get_list(filters)
            self.assertEqual(len(users), 1)
            self.assertEqual(users[0].username, 'lindas')

    def test_05_user_retrieve(self):
        """Test User.retrieve() method"""
        with self.app.app_context():
            filters = {'username': 'johne'}
            users = User.get_list(filters)
            self.assertEqual(len(users), 1)
            user = User.retrieve(users[0].userid)
            self.assertIsNotNone(user)
            self.assertIsInstance(user, User)
            self.assertEqual(users[0].username, user.username)

    def test_06_create_user_with_duplicate_name(self):
        """Test User create with duplicate name"""
        with self.app.app_context():
            with self.assertRaises(Exception):
                duplicate = User(
                    username='johne',
                    firstname='John',
                    lastname='Example',
                    email='johne@example.com',
                    phone='123-444-5555'
                )

    def test_07_update_user(self):
        """Test User.retrieve() method"""
        with self.app.app_context():
            filters = {'username': 'johne'}
            users = User.get_list(filters)
            self.assertEqual(len(users), 1)
            user = User.retrieve(users[0].userid)
            user.update(lastname='example')
            user = User.retrieve(users[0].userid)
            self.assertEqual(users[0].username, user.username)
            self.assertEqual(user.lastname, 'example')
            user.update(lastname='Example')


    def test_08_remove_user(self):
        """Test User.remove() method"""
        with self.app.app_context():
            filters = {'username': 'removeme'}
            users = User.get_list(filters)
            self.assertEqual(len(users), 1)
            users[0].remove()
            users = User.get_list(filters)
            self.assertEqual(len(users), 0)

    def test_09_set_password(self):
        """Test User.set_password() method"""
        with self.app.app_context():
            filters = {'username': 'johne'}
            users = User.get_list(filters)
            self.assertEqual(len(users), 1)
            users[0].set_password('pass')
            user = User.retrieve(users[0].userid)
            self.assertEqual(user.password, 'pass')

    def test_10_lock(self):
        """Test User lock methods"""
        with self.app.app_context():
            filters = {'username': 'johne'}
            users = User.get_list(filters)
            self.assertEqual(len(users), 1)
            users[0].set_lock()
            user = User.retrieve(users[0].userid)
            self.assertTrue(user.get_lock())
            user.unlock()
            user = User.retrieve(users[0].userid)
            self.assertFalse(user.get_lock())
            self.assertEqual(user.failed_logins, 0)
            self.assertIsNone(user.last_failed_login)

    def test_11_admin(self):
        """Test User admin methods"""
        with self.app.app_context():
            filters = {'username': 'johne'}
            users = User.get_list(filters)
            self.assertEqual(len(users), 1)
            users[0].grant_admin()
            user = User.retrieve(users[0].userid)
            self.assertTrue(user.get_admin())
            user.revoke_admin()
            user = User.retrieve(users[0].userid)
            self.assertFalse(user.get_admin())

    def test_12_user_get_list_pagination(self):
        """Test User.get_list() pagination filters"""
        with self.app.app_context():
            # Database should contain johne, lindas and lin
            filters = {'sortBy': '-lastname', 'offset': 1, 'limit': 2}
            users = User.get_list(filters)
            self.assertEqual(len(users), 2)
            self.assertEqual(users[0].username, 'lin')
