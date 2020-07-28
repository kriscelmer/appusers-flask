"""User Resource Implementation module

This module declares a Flask Blueprint of User Resources,
as well as all Operations related to:

    - Users Collection
    - User Document
    - Controllers associated with User Resources

Blueprint is registered in Application Factory function.
"""

from flask import Blueprint, request, jsonify, make_response, url_for, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from marshmallow import ValidationError
from appusers.models import (user_schema, user_list_schema,
    users_filters_schema, UserListSchema, set_password_body_schema)
from appusers.database import User
from appusers.utils import json_body, api_key_required, admin_required


# Create Users enpoint Blueprint
bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('', methods=['GET'])
@api_key_required
def list_users():
    """
    List and filter Users Collection

    Args:
        request.args - Query String parameters: filtering, sorting
            and pagination
        X-API-Key in request.headers

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
@jwt_required
@admin_required
@json_body(schema=user_schema)
def create_user(data):
    """
    Create User Resource

    Args:
        data - dictionary with all User Resource attributes, loaded from
            Request body JSON and validated with models.user_schema
        JWT Baerer Authorization in request.headers - admin privilege required

    Returns:
        Confirmation or Error Message
        'Location' Response Header
    """
    if User.get_list({'username': data['username']}):
        current_app.logger.warning(
            f'create_user() failed. Username={data["username"]} already exists'
            )
        return make_response('Bad request', 400)

    # Ignore 'userid' if present in request data
#    if 'userid' in data:
#        del(data['userid'])
#
    new_user = User(**data)

    response = make_response('Created', 201)
    response.headers['Location'] = url_for(
        'users.retrieve_user',
        userid=new_user.userid,
        _external=True
        )

    return response

@bp.route('/<int:userid>', methods=['GET'])
@api_key_required
def retrieve_user(userid):
    """
    Retrieve User Resource Representation

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)
        X-API-Key in request.headers

    Returns:
        JSON Object with User Resource Representation or Error Message
    """
    user = User.retrieve(userid)
    if user:
        return jsonify(user_schema.dump(user))
    else:
        return("Not Found", 404)

@bp.route('/<int:userid>', methods=['PUT'])
@jwt_required
@json_body(schema=user_schema)
def replace_user(userid, data):
    """
    Replace User Resource Representation

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)
        data - dictionary with all User Resource attributes, loaded from
            Request body JSON and validated with models.user_schema
        JWT Baerer Authorization in request.headers - account owner or
            admin privilege required

    Returns:
        Confirmation or Error Message
    """
    user = User.retrieve(userid)
    if not user:
        return make_response('Not found', 404)

    if User.get_list({'username': data['username']}):
        current_app.logger.warning(
            f'create_user() failed. Username={data["username"]} already exists'
            )
        return make_response('Bad request', 400)

    if current_user.userid != userid and not current_user.get_admin():
        current_app.logger.warning(
            f'replace_user(userid={userid}) failed. Userid={current_user.userid} not authorized'
            )
        return make_response('Unauthorized', 401)

    user.update(**data)

    return make_response('OK', 200)

@bp.route('/<int:userid>', methods=['PATCH'])
@jwt_required
@json_body(schema=user_schema, partial=True)
def update_user(userid, data):
    """
    Update User Resource Representation

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)
        data - dictionary with partial User Resource attributes, loaded from
            Request body JSON and validated with models.user_schema
        JWT Baerer Authorization in request.headers - account owner or
            admin privilege required

    Returns:
        Confirmation or Error Message
    """
    user = User.retrieve(userid)
    if not user:
        return make_response('Not found', 404)

    if 'username' in data and User.get_list({'username': data['username']}):
        current_app.logger.warning(
            f'create_user() failed. Username={data["username"]} already exists'
            )
        return make_response('Bad request', 400)

    if current_user.userid != userid and not current_user.get_admin():
        current_app.logger.warning(
            f'update_user(userid={userid}) failed. Userid={current_user.userid} not authorized'
            )
        return make_response('Unauthorized', 401)

    user.update(**data)

    return make_response('OK', 200)

@bp.route('/<int:userid>', methods=['DELETE'])
@jwt_required
@admin_required
def delete_user(userid):
    """
    Delete User Resource

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)
        JWT Baerer Authorization in request.headers - admin privilege required

    Returns:
        Confirmation or Error Message
    """
    user = User.retrieve(userid)
    if user:
        if userid == current_user.userid:
            current_app.logger.warning(
                f'delete_user(userid={userid}) failed. Cannot delete self'
                )
            return make_response('Unauthorized', 401)
        else:
            user.remove()
            return make_response('OK', 200)
    else:
        return make_response('Not found', 404)

@bp.route('/<int:userid>/set-password', methods=['POST'])
@jwt_required
@json_body(schema=set_password_body_schema)
def set_password(userid, data):
    """
    Set new password for User account

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)
        data - dictionary with Set new password for User attributes, loaded from
            Request body JSON and validated with models.set_password_body_schema
        JWT Baerer Authorization in request.headers - account owner or
            admin privilege required

    Returns:
        Confirmation or Error Message
    """
    user = User.retrieve(userid)
    if not user:
        return('Not Found', 404)

    if current_user.userid != userid and not current_user.get_admin():
        current_app.logger.warning(
            f'set_password(userid={userid}) failed. Userid={current_user.userid} not authorized'
            )
        return make_response('Unauthorized', 401)

    user.set_password(data['password'])

    return('OK', 200)

@bp.route('/<int:userid>/lock', methods=['GET'])
@jwt_required
@admin_required
def read_lock_status(userid):
    """
    Read User account lock status

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)
        JWT Baerer Authorization in request.headers - admin privilege required

    Returns:
        JSON Object with lock status or Error Message
    """
    user = User.retrieve(userid)
    if not user:
        return('Not Found', 404)

    return jsonify({'locked': user.get_lock()})

@bp.route('/<int:userid>/lock/set', methods=['POST'])
@jwt_required
@admin_required
def set_lock(userid):
    """
    Set User lock status

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)
        JWT Baerer Authorization in request.headers - admin privilege required

    Returns:
        Confirmation or Error Message
    """
    user = User.retrieve(userid)
    if not user:
        return('Not Found', 404)

    user.set_lock()
    return('OK', 200)

@bp.route('/<int:userid>/lock/unset', methods=['POST'])
@jwt_required
@admin_required
def clear_lock(userid):
    """
    Clear User lock status

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)
        JWT Baerer Authorization in request.headers - admin privilege required

    Returns:
        Confirmation or Error Message
    """
    user = User.retrieve(userid)
    if not user:
        return('Not Found', 404)

    user.unlock()
    return('OK', 200)

@bp.route('/<int:userid>/admin', methods=['GET'])
@jwt_required
@admin_required
def read_admin_status(userid):
    """
    Read User account admin privilege status

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)
        JWT Baerer Authorization in request.headers - admin privilege required

    Returns:
        JSON Object with admin status or Error Message
    """
    user = User.retrieve(userid)
    if not user:
        return('Not Found', 404)

    return jsonify({'isAdmin': user.get_admin()})

@bp.route('/<int:userid>/admin/grant', methods=['POST'])
@jwt_required
@admin_required
def grant_admin_status(userid):
    """
    Grant admin privilege to User

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)
        JWT Baerer Authorization in request.headers - admin privilege required

    Returns:
        Confirmation or Error Message
    """
    user = User.retrieve(userid)
    if not user:
        return('Not Found', 404)

    user.grant_admin()
    return('OK', 200)

@bp.route('/<int:userid>/admin/revoke', methods=['POST'])
@jwt_required
@admin_required
def remoke_admin_status(userid):
    """
    Revoke admin privilege from User

    Args:
        userid: Path Parameter - Unique ID of User Resource (int)
        JWT Baerer Authorization in request.headers - admin privilege required

    Returns:
        Confirmation or Error Message
    """
    user = User.retrieve(userid)
    if not user:
        return('Not Found', 404)

    user.revoke_admin()
    return('OK', 200)
