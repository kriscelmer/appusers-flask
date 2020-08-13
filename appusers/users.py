"""User Resource Implementation module

This module declares a Flask Blueprint of User Resources,
as well as all Operations related to:

    - Users Collection
    - User Document
    - Controllers associated with User Resources

Blueprint is registered in Application Factory function.
"""

from flask import Blueprint, request, jsonify, make_response, url_for
from appusers.database import User
from appusers.schema import user_schema, user_list_schema


# Create Users enpoint Blueprint
bp = Blueprint('users', __name__, url_prefix='/users')

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
    list = User.get_list({})
    return jsonify(user_list_schema.dump(list))

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

    if not request.is_json:
        return make_response('Unsupported Media Type', 415)

    try:
        data = request.get_json()
    except Exception as e:
        return make_response('Bad request', 400)

    new_user = User(**data)
    response = make_response('Created', 201)
    response.headers['Location'] = url_for('users.retrieve_user',
        userid=new_user.userid)

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
    user = User.retrieve(userid)
    if user:
        return jsonify(user_schema.dump(user))
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
    user = User.retrieve(userid)
    if not user:
        return make_response('Not found', 404)

    if not request.is_json:
        return make_response(f'Unsupported Media Type', 415)

    try:
        data = request.get_json()
    except Exception as e:
        return make_response('Bad request', 400)

    user.update(**data)

    return make_response('OK', 200)

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
    user = User.retrieve(userid)
    if not user:
        return make_response('Not found', 404)

    if not request.is_json:
        return make_response(f'Unsupported Media Type', 415)

    try:
        data = request.get_json()
    except Exception as e:
        return make_response('Bad request', 400)

    user.update(**data)

    return make_response('OK', 200)

@bp.route('/<int:userid>', methods=['DELETE'])
def delete_user(userid):
    """
    Delete User Resource

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)

    Returns:
        Confirmation or Error Message
    """
    user = User.retrieve(userid)
    if user:
        user.remove()
        return make_response('OK', 200)
    else:
        return make_response('Not found', 404)

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
