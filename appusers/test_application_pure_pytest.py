"""Unit tests for full Application

This module provides example Unit tests accessing full application with
Flask Test Client using PyTest only.
Test functions are executed in order of code sequence (functions in top of
this file are executed before functions in bottom).
Unit test functions names should have 'test_' prefix and accept a positional
argument 'client' - Test Client of Flask current application.
'@pytest.fixture' decorator indicates a generator function, yielding
a Test Client.
"""
import os
import pytest
from appusers import create_app
from appusers.database import db, User, Group


# Module level set-up for all unit tests in this file
if 'APPUSERS_CONFIG' not in os.environ:
    os.environ['APPUSERS_CONFIG'] = 'test_config.py'

app = create_app()
with app.app_context():
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

# End of module level set-up

def login(client, username, password):
    """Login helper function

    User login with application test client.

    Arguments:
        client - Flask Test Client
        username - string with username
        password - string with password

    Returns:
        JWT Token obtained from User Login operation
    """
    login_data = {'username': username, 'password': password}
    resp = client.post('/login', json=login_data)
    assert resp.status_code == 200
    resp_data = resp.get_json()
    return resp_data['jwtToken']

@pytest.fixture
def client():
    """Generator function yielding Test Client

    This function is called to yield a Test Client for each individual
    unit test declared in this module.
    Eventual set-up is executed before each test function and clean-up
    after each test function.
    """
    # Individual unit test set-up goes here, before 'yield' statement
    yield app.test_client()
    # Individual unit test clean-up goes here, after 'yield' statement

def test_list_users(client):
    """Simple test of List User Resources operation"""
    resp = client.get('/users', headers={'X-API-Key': app.config['API_KEY']})
    users = resp.get_json()
    assert resp.status_code == 200
    assert len(users) == 1
    assert users[0]['username'] == 'admin'

def test_add_user(client):
    """Example test of Create User Resource operation"""
    jwt_token = login(client, 'admin', 'pass')
    new_user = {
        'username': 'johne',
        'firstname': 'John',
        'lastname': 'Example',
        'email': 'johne@example.com',
        'phone': '123-444-5555'
    }
    resp = client.post(
        '/users',
        json=new_user,
        headers={'Authorization': 'Bearer '+jwt_token}
        )
    assert resp.status_code == 201

# Module level clean-up after all unit tests in this file
# End of module level clean-up
