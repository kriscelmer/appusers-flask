"""Login Resource Implementation module

This module declares a Flask Blueprint of Login Resource
as well as Login Operations.

Blueprint is registered in Application Factory function.
"""

from flask import Blueprint, jsonify, make_response


# Create Login enpoint Blueprint
bp = Blueprint('login', __name__, url_prefix='/login')

@bp.route('', methods=['POST'])
def login():
    """
    Login operation

    Args:
        request.body - JSON formatted username and password

    Returns:
        JSON with JWT Token and User link or Error Message
    """
    response = {'jwtToken': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOjF9.1HpgM-mGLjlZidENBpt3wQ4T7E-JXlvZ44JkHuoLeNk',
                'userHref': '/users/1'}
    return response, 200
