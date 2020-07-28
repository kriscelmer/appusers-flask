"""Unit tests for full Application

This module provides example Unit tests testing full application with
Flask Test Client.
"""
import os, unittest, time, datetime, pytest, flask_jwt_extended
from flask import url_for
from appusers import create_app
from appusers.database import db, User, Group


class TestApplicationClass(unittest.TestCase):
    """Test full Application"""

    @classmethod
    def setUpClass(cls):
        """Initialize app and create test_client"""

        if 'APPUSERS_CONFIG' not in os.environ:
            os.environ['APPUSERS_CONFIG'] = 'test_config.py'

        cls.app = create_app()
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            # Clear existing data in test database
            meta = db.metadata
            for table in reversed(meta.sorted_tables):
                db.session.execute(table.delete())
            db.session.commit()
            # Create user with admin privilege
            admin_user = User(
                username='admin',
                firstname='Admin',
                lastname='User',
                email='admin@example.com',
                phone='123-444-5555'
                )
            admin_user.set_password('pass')
            admin_user.grant_admin()
            # Create other Users and Groups
            johne = User(
                username='johne',
                firstname='John',
                lastname='Example',
                email='johne@example.com',
                phone='123-444-6666'
                )
            lindas = User(
                username='lindas',
                firstname='Linda',
                lastname='Sample',
                email='lindas@example.com',
                phone='123-444-7777'
                )
            lindas.set_password('pass')
            lin = User(
                username='lin',
                firstname='Li',
                lastname='Nerd',
                email='lin@example.com',
                phone='123-444-8888'
            )
            locked = User(
                username='locked',
                firstname='Locked',
                lastname='Account',
                email='locked@example.com',
                phone='123-444-9999'
                )
            locked.set_password('pass')
            locked.set_lock()
            devs = Group(
                groupname='devs',
                description='Developers'
                )
            testers = Group(
                groupname='testers',
                description='Testers'
            )

    def login(self, username, password):
        """Login username and return JWT Token"""
        login_data = {'username': username, 'password': password}
        resp = self.client.post(
            '/login',
            json=login_data
            )
        self.assertEqual(resp.status_code, 200)
        resp_data = resp.get_json()
        return resp_data['jwtToken']

    def test_1_login(self):
        """Test Login operation"""
        # This test assumes that 'admin' and 'lindas' are in Users,
        # both have password 'pass', are unlocked and can login
        # 'admin' must have following values:
        # username : admin
        # firstname : Admin
        # lastname : User
        # email: admin@example.com
        # phone : 123-444-5555
        # Test assumes user 'locked' is in Database with password 'pass',
        # is locked and unable to login
        # Test assumes there is no user 'admin1' in Database
        # Test assumes application configuration parameters
        # MAX_FAILED_LOGIN_ATTEMPTS and JWT_ACCESS_TOKEN_EXPIRES are set
        #
        # Test successful login operation - 200
        admin_login_data = {'username': 'admin', 'password': 'pass'}
        resp = self.client.post(
            '/login',
            json=admin_login_data
            )
        self.assertEqual(resp.status_code, 200)
        # Assert response data is JSON
        self.assertTrue(resp.is_json)
        resp_data = resp.get_json()
        # Assert Response JSON has expected fields
        self.assertSetEqual(
            {'jwtToken', 'userHref'},
            set(resp_data.keys())
            )
        # Decode and check returned JWT
        with self.app.app_context():
            decoded_token = flask_jwt_extended.decode_token(resp_data['jwtToken'])
        # Assert JWT has 'identity', 'iat' and 'exp' fields
        self.assertIn('identity', decoded_token)
        self.assertIn('iat', decoded_token)
        self.assertIn('exp', decoded_token)
        # Assert DB object with userid==decoded_token['identity'] is in fact 'admin'
        with self.app.app_context():
            user = User.retrieve(decoded_token['identity'])
        self.assertEqual(user.username, 'admin')
        # Assert JWT expiration 'exp' is set to Application Config value
        config_jwt_exp = self.app.config['JWT_ACCESS_TOKEN_EXPIRES']
        if type(config_jwt_exp) is int:
            self.assertEqual(
                decoded_token['exp'] - decoded_token['iat'],
                config_jwt_exp
                )
        elif type(config_jwt_exp) is datetime.timedelta:
            self.assertEqual(
                datetime.timedelta(
                    seconds=decoded_token['exp'] - decoded_token['iat']
                    ),
                config_jwt_exp
                )
        else:
            # We have unsupported type of JWT_ACCESS_TOKEN_EXPIRES.
            # flask_jwt_extended.create_token() should fail in this case,
            # resulting in failure of first Login operation.
            # Code below should not get reached
            self.fail(msg=f'Config parameter JWT_ACCESS_TOKEN_EXPIRES has unexpected type {type(config_jwt_exp)}')
        # Assert 'userHref' is 'admin' User URI
        resp1 = self.client.get(
            resp_data['userHref'],
            headers={'X-API-Key': self.app.config['API_KEY']}
            )
        self.assertEqual(resp1.status_code, 200)
        resp1_data = resp1.get_json()
        expected_admin_data = {
            'userid': user.userid,
            'username': 'admin',
            'firstname': 'Admin',
            'lastname': 'User',
            'contactInfo': {
                'email': 'admin@example.com',
                'phone': '123-444-5555'
                    }
                }
        self.assertDictEqual(resp1_data, expected_admin_data)

        # Test correct username and incorrect password - 401
        bad_pass_login_data = {'username': 'admin', 'password': 'pass1'}
        resp = self.client.post(
            '/login',
            json=bad_pass_login_data
            )
        self.assertEqual(resp.status_code, 401)
        # Assert no JSON in response data
        self.assertFalse(resp.is_json)
        self.assertIsNone(resp.get_json())

        # Test incorrect username - 401
        bad_username_login_data = {'username': 'admin1', 'password': 'pass1'}
        resp = self.client.post(
            '/login',
            json=bad_username_login_data
            )
        self.assertEqual(resp.status_code, 401)
        # Assert no JSON in response data
        self.assertFalse(resp.is_json)
        self.assertIsNone(resp.get_json())

        # Test locked account - 401
        locked_login_data = {'username': 'locked', 'password': 'pass'}
        resp = self.client.post(
            '/login',
            json=locked_login_data
            )
        self.assertEqual(resp.status_code, 401)
        # Assert no JSON in response data
        self.assertFalse(resp.is_json)
        self.assertIsNone(resp.get_json())

        # Test incorrect Request body data - 400
        bad_login_data = [
            {'user': 'admin', 'password': 'pass'},
            {'username': 'admin'},
            {'username': 'admin', 'password': 5},
            {'username': "admin'--", 'password': ''}
            ]
        for data in bad_login_data:
            resp = self.client.post(
                '/login',
                json=data
                )
            self.assertEqual(resp.status_code, 400,
                msg=f'bad_login_data={bad_login_data}')
            # Assert no JSON in response data
            self.assertFalse(resp.is_json,
                msg=f'bad_login_data={bad_login_data}')
            self.assertIsNone(resp.get_json(),
                msg=f'bad_login_data={bad_login_data}')

        # Test invalid JSON format data
        bad_json = '{"username": "admin", "password": "pass"'
        resp = self.client.post(
            '/login',
            data=bad_json,
            headers={'Content-Type': 'application/json'}
            )
        self.assertEqual(resp.status_code, 400)
        # Assert no JSON in response data
        self.assertFalse(resp.is_json)
        self.assertIsNone(resp.get_json())

        # Test 'text/plain' Request body format - 415
        text_data = 'random text'
        resp = self.client.post(
            '/login',
            data=text_data
            )
        self.assertEqual(resp.status_code, 415)
        # Assert no JSON in response data
        self.assertFalse(resp.is_json)
        self.assertIsNone(resp.get_json())

        # Test User account lock due to unsuccessful logins
        # Reset LOCK_TIMEOUT to very short period
        lock_timeout_config = self.app.config['LOCK_TIMEOUT']
        temporary_lock_timeout = 1
        self.app.config['LOCK_TIMEOUT'] = datetime.timedelta(
            seconds=temporary_lock_timeout
            )
        # Confirm User lindas is unlocked and can log in
        lindas_login_data = {'username': 'lindas', 'password': 'pass'}
        resp = self.client.post(
            '/login',
            json=lindas_login_data
            )
        self.assertEqual(resp.status_code, 200)
        # Make MAX_FAILED_LOGIN_ATTEMPTS failed login attempts
        # User account should not get locked yet
        incorrect_data = {'username': 'lindas', 'password': 'pass1'}
        for i in range(self.app.config['MAX_FAILED_LOGIN_ATTEMPTS']):
            resp = self.client.post(
                '/login',
                json=incorrect_data
                )
            self.assertEqual(resp.status_code, 401, msg=f'i={i}')
        # Make correct login to verify that account is not locked
        # and to clear failed logins counter
        resp = self.client.post(
            '/login',
            json=lindas_login_data
            )
        self.assertEqual(resp.status_code, 200)
        # Make MAX_FAILED_LOGIN_ATTEMPTS + 1 failed login attempts
        # User account should get locked in the end
        for i in range(self.app.config['MAX_FAILED_LOGIN_ATTEMPTS']+1):
            resp = self.client.post(
                '/login',
                json=incorrect_data
                )
            self.assertEqual(resp.status_code, 401, msg=f'i={i}')
        # Assert User cannot login now
        resp = self.client.post(
            '/login',
            json=lindas_login_data
            )
        self.assertEqual(resp.status_code, 401)
        # Sleep for temporary lock timeout (1 sec)
        time.sleep(temporary_lock_timeout)
        # Assert lindas can login again now
        resp = self.client.post(
            '/login',
            json=lindas_login_data
            )
        self.assertEqual(resp.status_code, 200)
        # Restore LOCK_TIMEOUT
        self.app.config['LOCK_TIMEOUT'] = lock_timeout_config

    def test_2_create_user(self):
        """Test Create User Resource operation"""
        # This test assumes 'admin' is in Database with password 'pass',
        # is unlocked and can log in, has admin privilege
        # Test assumes there are 4 other users in Database as well - total of 5
        # Test assumes there is no user 'testu' in Database
        # Test correct response - 200
        # Login as admin
        jwt_token = self.login('admin', 'pass')
        # Prepare new user dictionary with correct data
        # set userid to check if it is ignored
        testu = {
            'userid': 9999,
            'username': 'testu',
            'firstname': 'Test',
            'lastname': 'User',
            'contactInfo': {
                'email': 'testu@example.com',
                'phone': '123-444-0000'
                }
            }

        # Invoke Create User Resource operation
        resp1 = self.client.post(
            '/users',
            json=testu,
            headers={'Authorization': f'Bearer {jwt_token}'}
            )
        # Assert reponse is correct
        self.assertEqual(resp1.status_code, 201)

        # Check User Resource pointed by returned URI
        # Get New User URI
        self.assertIn('Location', resp1.headers)
        testu_uri = resp1.headers['Location']
        # Retrieve new User Resource
        resp2 = self.client.get(
            testu_uri,
            headers={'X-API-Key': self.app.config['API_KEY']}
            )
        # Assert new User Resource is correct
        self.assertEqual(resp2.status_code, 200)
        created_user = resp2.get_json()
        # Check if 'userid' in request data has got ignored
        self.assertNotEqual(created_user['userid'], 9999)
        # Add 'userid' from Location URI to johne dict
        testu_userid = testu_uri.split('/')[-1]
        testu_with_userid = testu.copy()
        testu_with_userid['userid'] = int(testu_userid)
        # Assert created user data in response is as expected
        self.assertDictEqual(testu_with_userid, created_user)

        # Test Unathorized response - 401
        bad_headers = [
            # Missing Authorization
            {},
            # X-API-Key instead of JWT Bearer token
            {'X-API-Key': self.app.config['API_KEY']},
            # invalid JWT Bearer token
            {'Authorization': f'Bearer invalid_token'}
            ]
        # Test bad authorization headers
        for headers in bad_headers:
            resp = self.client.post(
                '/users',
                json=testu,
                headers=headers
                )
            # Assert Status Code is 401
            self.assertEqual(resp.status_code, 401, msg=f'headers={headers}')
            # Assert no Location in response heders
            self.assertNotIn('Location', resp.headers)

        # Test Bad Request response - 400
        # Try to create 'testu' again
        resp = self.client.post(
            '/users',
            json=testu,
            headers={'Authorization': f'Bearer {jwt_token}'}
            )
        # Assert reponse is 400
        self.assertEqual(resp.status_code, 400)

        # Try incorrect data
        incorrect_data = [
            {
                'username': 'testu1',
                'firstname': 'Test',
                'lastname': 'User',
                'contactInfo': {
                    # missing email
                    'phone': '123-444-0000'
                    }
            },
            {
                'username': 'testu1',
                'firstname': 'Test',
                'lastname': 'User',
                'contactInfo': {
                    'email': 'wrong_email_address',
                    'phone': '123-444-0000'
                    }
            },
            {
                'username': '1testu', # invalid user name
                'firstname': 'Test',
                'lastname': 'User',
                'contactInfo': {
                    'email': 'testu@example.com',
                    'phone': '123-444-0000'
                    }
            }
            ]

        for data in incorrect_data:
            resp = self.client.post(
                '/users',
                json=data,
                headers={'Authorization': f'Bearer {jwt_token}'}
                )
            # Assert reponse is 400
            self.assertEqual(resp.status_code, 400, msg=f'data={data}')
            # Assert no Location in response heders
            self.assertNotIn('Location', resp.headers, msg=f'data={data}')

        # Assure there are exactly 6 Users in database now.
        # Get list of all users
        resp = self.client.get(
            '/users',
            headers={'X-API-Key': self.app.config['API_KEY']}
            )
        self.assertEqual(resp.status_code, 200)
        users = resp.get_json()
        self.assertEqual(len(users), 6)

    def test_3_retrieve_user(self):
        """Test Retrieve User Resource Representation operation"""
        # This test assumes 'admin' is in Database with password 'pass',
        # is unlocked and can log in, has admin privilege
        # Test expects User 'johne' in Database with following values:
        # username : johne
        # firstname : John
        # lastname : Example
        # email: johne@example.com
        # phone: 123-444-6666
        #
        # Test correct response - 200
        # Get 'johne' userid directly from Database
        with self.app.app_context():
            johne_userid = User.get_list({'username': 'johne'})[0].userid
        # Retrieve User Representation of 'johne'
        resp = self.client.get(
            f'/users/{johne_userid}',
            headers={'X-API-Key': self.app.config['API_KEY']}
            )
        self.assertEqual(resp.status_code, 200)
        # Assert response data is JSON
        self.assertTrue(resp.is_json)
        user_data = resp.get_json()
        # Assert response data is exactly what's expected
        johne = {
            'userid': johne_userid,
            'username': 'johne',
            'firstname': 'John',
            'lastname': 'Example',
            'contactInfo': {
                'email': 'johne@example.com',
                'phone': '123-444-6666'
                }
            }
        self.assertDictEqual(johne, user_data)

        # Test Unauthorized response - 401
        jwt_token = self.login('admin', 'pass')
        bad_headers = [
            # Missing Authorization header
            {},
            # Invalid X-API-Key
            {'X-API-Key': self.app.config['API_KEY'] + 'incorrect'},
            # valid JWT Bearer token instead of X-API-Key
            {'Authorization': f'Bearer {jwt_token}'}
            ]
        # Test bad authorization headers
        for headers in bad_headers:
            resp = self.client.get(
                f'/users/{johne_userid}',
                headers=headers
                )
            # Assert Status Code is 401
            self.assertEqual(resp.status_code, 401, msg=f'headers={headers}')

            # Assert no JSON in response data
            self.assertFalse(resp.is_json, msg=f'headers={headers}')
            self.assertIsNone(resp.get_json(), msg=f'headers={headers}')

        # Test response Not Found - 404
        # Find largest userid in Database and add 1
        with self.app.app_context():
            non_existent_userid = User.get_list({'sortBy': '-userid'})[0].userid + 1
        resp = self.client.get(
            f'/users/{non_existent_userid}',
            headers={'X-API-Key': self.app.config['API_KEY']}
            )
        self.assertEqual(resp.status_code, 404)
        # Assert no JSON in response data
        self.assertFalse(resp.is_json)
        self.assertIsNone(resp.get_json())

    def test_4_add_user_to_group(self):
        """Test Add User to Group operation"""
        # This test assumes following Database state:
        # admin and johne in Users; admin can login and has admin privilege
        # devs in Groups; devs has no members
        #
        # Add johne to group devs
        #
        # Get johne userid
        resp = self.client.get(
            '/users',
            query_string={'username': 'johne'},
            headers={'X-API-Key': self.app.config['API_KEY']}
            )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['username'], 'johne')
        johne_userid = data[0]['userid']
        # Get devs groupid
        resp = self.client.get(
            '/groups',
            query_string={'groupname': 'devs'},
            headers={'X-API-Key': self.app.config['API_KEY']}
            )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['groupname'], 'devs')
        devs_groupid = data[0]['groupid']
        # Login as admin
        jwt_token = self.login('admin', 'pass')
        resp = self.client.put(
            f'/groups/{devs_groupid}/members/{johne_userid}',
            headers={'Authorization': f'Bearer {jwt_token}'}
            )
        self.assertEqual(resp.status_code, 201)
        # Repeat Add User to Group operation to check if status code is 200
        resp = self.client.put(
            f'/groups/{devs_groupid}/members/{johne_userid}',
            headers={'Authorization': f'Bearer {jwt_token}'}
            )
        self.assertEqual(resp.status_code, 200)
        # Retrieve list of devs Group members to check if johne is a member
        resp = self.client.get(
            f'/groups/{devs_groupid}/members',
            headers={'X-API-Key': self.app.config['API_KEY']}
            )
        self.assertEqual(resp.status_code, 200)
        members = resp.get_json()
        self.assertGreater(len(members), 0)
        self.assertTrue(any(m['username'] == 'johne' for m in members))
