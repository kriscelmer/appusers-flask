"""Login Resource Implementation module

This module declares a Flask Blueprint of Login Resource
as well as Login Operations.
Blueprint is registered in Application Factory function.

jwt, the instance of JWTManager from Flask-JWT-Extended is declared here and
is initialized in Application Factory function.
jwt uses following Application Config variables declared in Application Factory:
- JWT_ACCESS_TOKEN_EXPIRES - number of seconds or timedelta,
    token expires (gets invalid) in this period fater creation
- JWT_SECRET_KEY - secret key needed for symmetric based signing algorithms,
    such as HS256 (default)
Check all Flask-JWT-Extended configration options at:
    https://flask-jwt-extended.readthedocs.io/en/stable/options/
"""
from datetime import datetime
from flask import Blueprint, url_for, jsonify, current_app, make_response
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.security import safe_str_cmp
from appusers.database import User
from appusers.models import login_body_schema
from appusers.utils import json_body


# JWT Manager object is initialized in Application Factory
jwt = JWTManager()

# Create Login enpoint Blueprint
bp = Blueprint('login', __name__, url_prefix='/login')

@bp.route('', methods=['POST'])
@json_body(schema=login_body_schema)
def login(data):
    """
    Login operation

    Args:
        data - dictionary with all Login operation attributes, loaded from
            Request body JSON and validated with models.login_body_schema

    Returns:
        JSON with JWT Token and User link or Error Message. Token contains
        'identity' field set to userid of authenticated User.
        Token expires after JWT_ACCESS_TOKEN_EXPIRES.
    """
    user_list = User.get_list({'username': data['username']})
    if len(user_list) == 0:
        current_app.logger.warning(
            f'authenticate_user() failed. No such user: {data["username"]}'
            )
        return make_response('Unathorized', 401)
    else:
        user = user_list[0]

    # check if User account is locked, lift lock if lock interval passed
    if user.last_failed_login and datetime.now() > user.last_failed_login + current_app.config['LOCK_TIMEOUT']:
        user.unlock()
        current_app.logger.info(
            f'authenticate_user() - userid={user.userid} unlocked due to lock timeout'
            )

    if user.get_lock():
        current_app.logger.warning(
            f'authenticate_user() failed. Userid={user.userid} is locked'
            )
        return make_response('Unathorized', 401)

    if safe_str_cmp(user.password.encode('utf-8'), data['password'].encode('utf-8')):
        # clear lock info on successful login
        user.unlock()
        access_token = create_access_token(identity=user.userid)
        response = {'jwtToken': access_token,
            'userHref': url_for(
                'users.retrieve_user',
                userid=user.userid,
                _external=True
                )}
        current_app.logger.info(
            f'authenticate_user() successful. {user.username} logged in'
            )
        return(jsonify(response), 200)
    else:
        current_app.logger.warning(
            f'authenticate_user() failed. Incorrect password for userid={user.userid}'
            )
        # update lock status
        user.failed_logins = user.failed_logins + 1
        user.last_failed_login = datetime.now() # consider datetime.utcnow()
        if user.failed_logins > current_app.config['MAX_FAILED_LOGIN_ATTEMPTS']:
            user.set_lock()
            current_app.logger.warning(
                f'Too many failed logins for userid={user.userid}, account locked'
                )
        user.update()
        return make_response('Unauthorized', 401)

# Callback functions for JWTManager

@jwt.user_loader_callback_loader
def load_current_user(identity):
    """Load User object for JWTManager, using Token's identity"""
    return User.retrieve(identity)

@jwt.user_loader_error_loader
def current_user_not_found(identity):
    """Return error Response due to User object for Token's identity not found"""
    current_app.logger.warning(
        f'User with JWT identity={identity} not found in Database!'
        )
    return make_response('Unathorized', 401)
