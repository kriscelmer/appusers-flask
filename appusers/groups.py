"""Group Resource Implementation module

This module declares a Flask Blueprint of Group Resources,
as well as all Operations related to:

    - Groups Collection
    - Group Document
    - Controllers associated with Group Resources

Blueprint is registered in Application Factory function.
"""

from flask import Blueprint, request, jsonify, make_response, url_for, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from appusers.models import (group_schema, group_list_schema,
    groups_filters_schema, GroupListSchema, group_members_filters_schema,
    user_list_schema, UserListSchema)
from appusers.database import Group, User
from appusers.utils import json_body, api_key_required, admin_required


# Create Groups enpoint Blueprint
bp = Blueprint('groups', __name__, url_prefix='/groups')

@bp.route('', methods=['GET'])
@api_key_required
def list_groups():
    """
    List and filter Groups Collection

    Args:
        request.args - Query String parameters: filtering, sorting
            and pagination
        X-API-Key in request.headers

    Returns:
        JSON array of Group Resource Representations or Error Message
    """
    try:
        filters = groups_filters_schema.load(request.args)
    except ValidationError as e:
        current_app.logger.warning(
            f'list_groups() Query String validation failed.\nValidationError: {e}'
            )
        return make_response('Bad request', 400)

    filtered_list = Group.get_list(filters)
    if 'return_fields' in filters:
        return_fields = filters['return_fields'].split(',') + ['href']
        groups = GroupListSchema(many=True, only=return_fields).dump(filtered_list)
    else:
        groups = group_list_schema.dump(filtered_list)
    return jsonify(groups)

@bp.route('', methods=['POST'])
@jwt_required
@admin_required
@json_body(schema=group_schema)
def create_group(data):
    """
    Create Group Resource

    Args:
        data - dictionary with all Group Resource attributes, loaded from
            Request body JSON and validated with models.group_schema
        JWT Baerer Authorization in request.headers - admin privilege required

    Returns:
        Confirmation or Error Message
        'Location' Response Header
    """
    if Group.get_list({'groupname': data['groupname']}):
        current_app.logger.warning(
            f'create_group() failed. Groupname={data["groupname"]} already exists'
            )
        return make_response('Bad request', 400)

    new_group =  Group(**data)

    response = make_response('Created', 201)
    response.headers['Location'] = url_for(
        'groups.retrieve_group',
        groupid=new_group.groupid,
        _external=True
        )

    return response

@bp.route('/<int:groupid>', methods=['GET'])
@api_key_required
def retrieve_group(groupid):
    """
    Retrieve Group Resource Representation

    Args:
        groupid: Path Parameter - Unique ID of Group Resource (int)
        X-API-Key in request.headers

    Returns:
        JSON Object with Group Resource Representation or Error Message
    """
    group = Group.retrieve(groupid)
    if group:
        return jsonify(group_schema.dump(group))
    else:
        return("Not Found", 404)

@bp.route('/<int:groupid>', methods=['PUT'])
@jwt_required
@admin_required
@json_body(schema=group_schema)
def replace_group(groupid, data):
    """
    Replace Group Resource Representation

    Args:
        groupid: Path Parameter - Unique ID of Group Resource (int)
        data - dictionary with all Group Resource attributes, loaded from
            Request body JSON and validated with models.group_schema
        JWT Baerer Authorization in request.headers - admin privilege required

    Returns:
        Confirmation or Error Message
    """
    group = Group.retrieve(groupid)
    if not group:
        return make_response('Not found', 404)

    if Group.get_list({'groupname': data['groupname']}):
        current_app.logger.warning(
            f'create_group() failed. Groupname={data["groupname"]} already exists'
            )
        return make_response('Bad request', 400)

    group.update(**data)

    return make_response('OK', 200)

@bp.route('/<int:groupid>', methods=['PATCH'])
@jwt_required
@admin_required
@json_body(schema=group_schema, partial=True)
def update_group(groupid, data):
    """
    Update Group Resource Representation

    Args:
        groupid: Path Parameter - Unique ID of Group Resource (int)
        data - dictionary with partial Group Resource attributes, loaded from
            Request body JSON and validated with models.group_schema
        JWT Baerer Authorization in request.headers - admin privilege required

    Returns:
        Confirmation or Error Message
    """
    group = Group.retrieve(groupid)
    if not group:
        return make_response('Not found', 404)

    if 'groupname' in data and Group.get_list({'groupname': data['groupname']}):
        current_app.logger.warning(
            f'create_group() failed. Groupname={data["groupname"]} already exists'
            )
        return make_response('Bad request', 400)

    group.update(**data)

    return make_response('OK', 200)

@bp.route('/<int:groupid>', methods=['DELETE'])
@jwt_required
@admin_required
def delete_group(groupid):
    """
    Delete Group Resource

    Args:
        groupid: Path Parameter - Unique ID of Group Resource (int)
        JWT Baerer Authorization in request.headers - admin privilege required

    Returns:
        Confirmation or Error Message
    """
    group = Group.retrieve(groupid)
    if group:
        try:
            group.remove()
        except Exception as e:
            current_app.logger.warning(
                f'delete_group(groupid={groupid}) failed.\nError: {e}'
                )
            make_response('Internal error', 500)
        else:
            return make_response('OK', 200)
    else:
        return make_response('Not found', 404)

@bp.route('/<int:groupid>/members', methods=['GET'])
@api_key_required
def list_group_members(groupid):
    """
    Retrieve Group members

    Args:
        groupid: Path Parameter - Unique ID of Group Resource (int)
        request.args - Query String parameters: fields
        X-API-Key in request.headers

    Returns:
        JSON array of User Resource Representations or Error Message
    """
    group = Group.retrieve(groupid)
    if group == None:
        current_app.logger.warning(
            f'list_group_members() Group with id={groupid} not found'
            )
        return make_response('Group not found', 404)

    try:
        filters = group_members_filters_schema.load(request.args)
    except ValidationError as e:
        current_app.logger.warning(
            f'list_group_members() Query String validation failed.\nValidationError: {e}'
            )
        return make_response('Bad request', 400)

    filtered_list = group.list_members()
    if 'return_fields' in filters:
        return_fields = filters['return_fields'].split(',') + ['href']
        users = UserListSchema(many=True, only=return_fields).dump(filtered_list)
    else:
        users = user_list_schema.dump(filtered_list)
    return jsonify(users)

@bp.route('/<int:groupid>/members/<int:userid>', methods=['PUT'])
@jwt_required
@admin_required
def add_user_to_group(groupid, userid):
    """
    Add User to Group

    Args:
        groupid: Path Parameter - Unique ID of Group Resource (int)
        userid: Path Parameter - Unique ID of User Resource (int)
        JWT Baerer Authorization in request.headers - admin privilege required

    Returns:
        Confirmation or Error Message
    """
    group = Group.retrieve(groupid)
    if group == None:
        current_app.logger.warning(
            f'add_user_to_group() Group with id={groupid} not found'
            )
        return make_response('Group or User not found', 404)
    user = User.retrieve(userid)
    if user == None:
        current_app.logger.warning(
            f'add_user_to_group() User with id={userid} not found'
            )
        return make_response('Group or User not found', 404)
    if user in group.users:
        return 'User already in the Group', 200
    else:
        group.add_member(user)
        return 'User added to the Group', 201

@bp.route('/<int:groupid>/members/<int:userid>', methods=['DELETE'])
@jwt_required
@admin_required
def delete_user_from_group(groupid, userid):
    """
    Delete User from Group

    Args:
        groupid: Path Parameter - Unique ID of Group Resource (int)
        userid: Path Parameter - Unique ID of User Resource (int)
        JWT Baerer Authorization in request.headers - admin privilege required

    Returns:
        Confirmation or Error Message
    """
    group = Group.retrieve(groupid)
    if group == None:
        current_app.logger.warning(
            f'add_user_to_group() Group with id={groupid} not found'
            )
        return make_response('Group or User not found', 404)
    user = User.retrieve(userid)
    if user == None:
        current_app.logger.warning(
            f'add_user_to_group() User with id={userid} not found'
            )
        return make_response('Group or User not found', 404)
    group.remove_member(user)
    return 'User deleted from Group', 200
