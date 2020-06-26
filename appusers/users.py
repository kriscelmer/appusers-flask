"""User Resource Implementation module

This module declares a Flask Blueprint of User Resources,
as well as all Operations related to:

    - Users Collection
    - User Document
    - Controllers associated with User Resources

Blueprint is registered in Application Factory function.
"""

from flask import Blueprint, request, jsonify, make_response, url_for
from appusers.models import User, user_schema, user_list_schema


# Create Users enpoint Blueprint
bp = Blueprint('users', __name__, url_prefix='/users')

# Initialize some data
johne = User(
    userid=0,
    username='johne',
    firstname='John',
    lastname='Example',
    email='johne@example.com',
    phone='123-444-5555'
    )
lindas = User(
    userid=1,
    username='lindas',
    firstname='Linda',
    lastname='Someone',
    email='lindas@example.com',
    phone='123.444.6666'
    )
users_list = {0: johne, 1: lindas}
users_max_index = 1

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
    list = users_list.values()
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
    global users_max_index

    if not request.is_json:
        return make_response('Unsupported Media Type', 415)

    try:
        data = request.get_json()
        users_max_index = users_max_index + 1
        data['userid'] = users_max_index
        new_user = user_schema.load(data)
    except Exception as e:
        users_max_index -= 1
        return make_response('Bad request', 400)

    users_list[users_max_index] = new_user
    response = make_response('Created', 201)
    response.headers['Location'] = url_for('users.retrieve_user', userid=new_user.userid)

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
    if userid in users_list:
        return jsonify(user_schema.dump(users_list[userid]))
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
    if userid not in users_list:
        return make_response('Not found', 404)

    if not request.is_json:
        return make_response(f'Unsupported Media Type', 415)

    try:
        data = request.get_json()
        data['userid'] = userid
        new_user = user_schema.load(data)
    except Exception as e:
        return make_response('Bad request', 400)

    users_list[userid] = new_user

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
    if userid in users_list:
        del users_list[userid]
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
