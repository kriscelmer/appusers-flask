"""User Resource Implementation module

This module declares a Flask Blueprint of User Resources,
as well as all Operations related to:

    - Users Collection
    - User Document
    - Controllers associated with User Resources

Blueprint is registered in Application Factory function.
"""

from flask import Blueprint, jsonify, make_response


# Create Users enpoint Blueprint
bp = Blueprint('users', __name__, url_prefix='/users')

# Initialize some data
users_list = [{'id': 0,
               'username': 'johne',
               'firstname': 'John',
               'lastname': 'Example',
               'contactInfo': {
                    'email': 'johne@example.com',
                    'phone': '123.444.5555'
                    }
               },
               {'id': 1,
                'username': 'lindas',
                'firstname': 'Linda',
                'lastname': 'Someone',
                'contactInfo': {
                    'email': 'lindas@example.com',
                    'phone': '123.444.6666'
                }
               }]

@bp.route('', methods=['GET'])
def list_users():
    """
    List and filter Users Collection

    Args:
        request.args - Query String parameters: filtering, sorting
            and pagination

    Returns:
        JSON array of User Resource Representations
    """
    return jsonify(users_list)

@bp.route('', methods=['POST'])
def create_user():
    """
    Create User Resource

    Args:
        request.body - JSON formatted User Resource attributes

    Returns:
        Confirmation or Error Message
        'Location' Response Header
    """
    response = make_response("Created", 201)
    response.headers['Location'] = '/users/0'
    return response

@bp.route('/<int:userid>', methods=['GET'])
def retrieve_user(userid):
    """
    Retrieve User Resource Representation

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)

    Returns:
        JSON Object with User Resource Representation or Error Message
    """
    if 0 <= userid and userid <= len(users_list):
        return jsonify(users_list[userid])
    else:
        return "Not Found", 404

@bp.route('/<int:userid>', methods=['PUT'])
def replace_user(userid):
    """
    Replace User Resource Representation

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)
        request.body - JSON formatted User Resource attributes

    Returns:
        Confirmation or Error Message
    """
    return "Replace User Resource Representation mock-up", 200

@bp.route('/<int:userid>', methods=['PATCH'])
def update_user(userid):
    """
    Update User Resource Representation

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)
        request.body - JSON formatted User Resource attributes

    Returns:
        Confirmation or Error Message
    """
    return "Update User Resource Representation mock-up", 200

@bp.route('/<int:userid>', methods=['DELETE'])
def delete_user(userid):
    """
    Delete User Resource

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)

    Returns:
        Confirmation or Error Message
    """
    return "Delete User Resource mock-up", 200

@bp.route('/<int:userid>/set-password', methods=['POST'])
def set_password(userid):
    """
    Set new password for User account

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)
        request.body - JSON formatted password attributes

    Returns:
        Confirmation or Error Message
    """
    return "Set new password for User account mock-up", 200

@bp.route('/<int:userid>/lock', methods=['GET'])
def read_lock_status(userid):
    """
    Read User account lock status

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)

    Returns:
        JSON Object with lock status or Error Message
    """
    return "Read User account lock status mock-up", 200

@bp.route('/<int:userid>/lock/set', methods=['POST'])
def set_lock(userid):
    """
    Set User lock status

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)

    Returns:
        Confirmation or Error Message
    """
    return "Set User lock status mock-up", 200

@bp.route('/<int:userid>/lock/unset', methods=['POST'])
def clear_lock(userid):
    """
    Clear User lock status

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)

    Returns:
        Confirmation or Error Message
    """
    return "Clear User lock status mock-up", 200

@bp.route('/<int:userid>/admin', methods=['GET'])
def read_admin_status(userid):
    """
    Read User account admin privilege status

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)

    Returns:
        JSON Object with admin status or Error Message
    """
    return "Read User account admin privilege status mock-up", 200

@bp.route('/<int:userid>/admin/grant', methods=['POST'])
def grant_admin_status(userid):
    """
    Grant admin privilege to User

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)

    Returns:
        Confirmation or Error Message
    """
    return "Grant admin privilege to User mock-up", 200

@bp.route('/<int:userid>/admin/revoke', methods=['POST'])
def remoke_admin_status(userid):
    """
    Revoke admin privilege from User

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)

    Returns:
        Confirmation or Error Message
    """
    return "Revoke admin privilege from User mock-up", 200
