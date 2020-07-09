"""User Resource Implementation module

This module declares a Flask Blueprint of User Resources,
as well as all Operations related to:

    - Users Collection
    - User Document
    - Controllers associated with User Resources

Blueprint is registered in Application Factory function.
"""

from flask import Blueprint, request, jsonify, make_response, url_for, current_app
from marshmallow import ValidationError
from appusers.models import user_schema, user_list_schema, users_filters_schema, UserListSchema, set_password_body_schema
from appusers.database import User
from appusers.utils import json_body


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
    try:
        filters = users_filters_schema.load(request.args)
    except ValidationError as e:
        current_app.logger.warning(
            f'list_group() Query String validation failed.\nValidationError: {e}'
            )
        return make_response('Bad request', 400)

    filtered_list = User.get_list(filters)
    if 'return_fields' in filters:
        return_fields = filters['return_fields'].split(',') + ['href']
        users = UserListSchema(many=True, only=return_fields).dump(filtered_list)
    else:
        users = user_list_schema.dump(filtered_list)
    return jsonify(users)

@bp.route('', methods=['POST'])
@json_body
def create_user(data):
    """
    Create User Resource

    Args:
        request.body - JSON formatted User Resource attributes

    Returns:
        Confirmation or Error Message
        'Location' Response Header
    """
    try:
        new_user_data = user_schema.load(data)
        new_user = User(**new_user_data)
    except Exception as e:
        current_app.logger.warning(
            f'create_user() failed.\nError: {e}'
            )
        return make_response('Bad request', 400)

    response = make_response('Created', 201)
    response.headers['Location'] = url_for(
        'users.retrieve_user',
        userid=new_user.userid
        )

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
        return("Not Found", 404)

@bp.route('/<int:userid>', methods=['PUT'])
@json_body
def replace_user(userid, data):
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

    try:
        new_user_data = user_schema.load(data)
        user.update(**new_user_data)
    except Exception as e:
        current_app.logger.warning(
            f'replace_user(userid={userid}) failed.\nError: {e}'
            )
        return make_response('Bad request', 400)

    return make_response('OK', 200)

@bp.route('/<int:userid>', methods=['PATCH'])
@json_body
def update_user(userid, data):
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

    try:
        new_user_data = user_schema.load(data, partial=True)
        user.update(**new_user_data)
    except Exception as e:
        current_app.logger.warning(
            f'upate_user(userid={userid}) failed.\nError: {e}'
            )
        return make_response('Bad request', 400)

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
        try:
            user.remove()
        except Exception as e:
            current_app.logger.warning(
                f'delete_user(userid={userid}) failed.\nError: {e}'
                )
            return make_response('Internal error', 500)
        else:
            return make_response('OK', 200)
    else:
        return make_response('Not found', 404)

@bp.route('/<int:userid>/set-password', methods=['POST'])
@json_body
def set_password(userid, data):
    """
    Set new password for User account

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)
        request.body - JSON formatted password attributes

    Returns:
        Confirmation or Error Message
    """
    user = User.retrieve(userid)
    if not user:
        return('Not Found', 404)

    try:
        passwords = set_password_body_schema.load(data)
        user.set_password(passwords['password'])
    except Exception as e:
        current_app.logger.warning(
            f'set_password(userid={userid}) failed.\nError: {e}'
            )
        return make_response('Bad Request', 400)

    return('OK', 200)

@bp.route('/<int:userid>/lock', methods=['GET'])
def read_lock_status(userid):
    """
    Read User account lock status

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)

    Returns:
        JSON Object with lock status or Error Message
    """
    user = User.retrieve(userid)
    if not user:
        return('Not Found', 404)

    return jsonify({'locked': user.get_lock()})

@bp.route('/<int:userid>/lock/set', methods=['POST'])
def set_lock(userid):
    """
    Set User lock status

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)

    Returns:
        Confirmation or Error Message
    """
    user = User.retrieve(userid)
    if not user:
        return('Not Found', 404)

    user.set_lock()
    return('OK', 200)

@bp.route('/<int:userid>/lock/unset', methods=['POST'])
def clear_lock(userid):
    """
    Clear User lock status

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)

    Returns:
        Confirmation or Error Message
    """
    user = User.retrieve(userid)
    if not user:
        return('Not Found', 404)

    user.unlock()
    return('OK', 200)

@bp.route('/<int:userid>/admin', methods=['GET'])
def read_admin_status(userid):
    """
    Read User account admin privilege status

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)

    Returns:
        JSON Object with admin status or Error Message
    """
    user = User.retrieve(userid)
    if not user:
        return('Not Found', 404)

    return jsonify({'isAdmin': user.get_admin()})

@bp.route('/<int:userid>/admin/grant', methods=['POST'])
def grant_admin_status(userid):
    """
    Grant admin privilege to User

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)

    Returns:
        Confirmation or Error Message
    """
    user = User.retrieve(userid)
    if not user:
        return('Not Found', 404)

    user.grant_admin()
    return('OK', 200)

@bp.route('/<int:userid>/admin/revoke', methods=['POST'])
def remoke_admin_status(userid):
    """
    Revoke admin privilege from User

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)

    Returns:
        Confirmation or Error Message
    """
    user = User.retrieve(userid)
    if not user:
        return('Not Found', 404)

    user.revoke_admin()
    return('OK', 200)
