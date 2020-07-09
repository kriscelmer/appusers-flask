"""Utility functions and decorators module

This module declares utility functions and decorators:

    - json_body - checks if Request body is in JSON format and optionally
                  validates it against Marshmallow schema (model)
    - api_key_required - checks if Request headers contain X-API-Key and
                         compares its value to Application Configuration
                         variable API_KEY (declared in Application Factory)
    - admin_required - checks if JWT Bearer token in current Request has
                       identity of User with admin privilege
"""
from functools import wraps
from werkzeug.security import safe_str_cmp
from flask import request, make_response, current_app
from flask_jwt_extended import get_current_user
from appusers.database import User


def json_body(_func=None, *, schema=None, partial=False):
    """Checks if Request Body is a JSON and loads it to data parameter added to
       invocation of wrapped function. Wrapped function must accept data
       parameter, which has a dictionary type value.
       Optionaly validates data with Marshmallow schema (model).
       Validation may be partial.
    """
    def decorator_json_body(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return make_response('Unsupported Media Type', 415)
            try:
                raw_data = request.get_json()
                if schema:
                    data = schema.load(raw_data, partial=partial)
                else:
                    data = raw_data
            except Exception as e:
                current_app.logger.warning(
                    f'{f.__name__}() failed. Request body JSON invalid\nError: {e}'
                    )
                return make_response('Bad request', 400)
            return f(*args, data=data, **kwargs)
        return decorated_function

    if _func is None:
        return decorator_json_body
    else:
        return decorator_json_body(_func)

def api_key_required(f):
    """Checks if Request header X-API-Key is present and has correct value"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        header = request.headers.get('X-API-Key', '')
        config = current_app.config.get('API_KEY', '')
        if safe_str_cmp(header.encode('utf-8'), config.encode('utf-8')):
            return f(*args, **kwargs)
        else:
            return make_response('Unauthorized', 401)
    return decorated_function

def admin_required(f):
    """Checks if User with JWT Identity has admin privilege"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user.get_admin():
            current_app.logger.warning(
                f'{f.__name__}() failed. userid={user.userid} is not admin'
                )
            return make_response('Unathorized', 401)
        return f(*args, **kwargs)
    return decorated_function
