"""Utility functions and decorators module

This module declares utility functions and decorators:

    - json_body
"""
from functools import wraps
from flask import request, make_response

def json_body(f):
    """Checks if Request Body is JSON and loads it to data parameter"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return make_response('Unsupported Media Type', 415)
        try:
            data = request.get_json()
        except Exception as e:
            return make_response('Bad request', 400)
        return f(*args, data=data, **kwargs)
    return decorated_function
