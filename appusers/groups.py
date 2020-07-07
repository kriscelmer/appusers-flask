"""Group Resource Implementation module

This module declares a Flask Blueprint of Group Resources,
as well as all Operations related to:

    - Groups Collection
    - Group Document
    - Controllers associated with Group Resources

Blueprint is registered in Application Factory function.
"""

from flask import Blueprint, request, jsonify, make_response, url_for, current_app
from marshmallow import ValidationError
from appusers.models import group_schema, group_list_schema, groups_filters_schema
from appusers.database import Group
from appusers.utils import json_body


# Create Groups enpoint Blueprint
bp = Blueprint('groups', __name__, url_prefix='/groups')

@bp.route('', methods=['GET'])
def list_groups():
    """
    List and filter Groups Collection

    Args:
        request.args - Query String parameters: filtering, sorting
            and pagination

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

    current_app.logger.info(
        f'list_groups(): Validated filters are: {filters}'
        )

    filtered_list = Group.get_list(filters)
    return jsonify(group_list_schema.dump(filtered_list))

@bp.route('', methods=['POST'])
@json_body
def create_group(data):
    """
    Create Group Resource

    Args:
        request.body - JSON formatted Group Resource attributes

    Returns:
        Confirmation or Error Message
        'Location' Response Header
    """
    try:
        new_group_data = group_schema.load(data)
        new_group =  Group(**new_group_data)
    except Exception as e:
        current_app.logger.warning(
            f'create_group() failed.\nError: {e}'
            )
        return make_response('Bad request', 400)

    response = make_response('Created', 201)
    response.headers['Location'] = url_for(
        'groups.retrieve_group',
        groupid=new_group.groupid
        )

    return response

@bp.route('/<int:groupid>', methods=['GET'])
def retrieve_group(groupid):
    """
    Retrieve Group Resource Representation

    Args:
        groupid: Path Parameter - Unique ID of Group Resource (int)

    Returns:
        JSON Object with Group Resource Representation or Error Message
    """
    group = Group.retrieve(groupid)
    if group:
        return jsonify(group_schema.dump(group))
    else:
        return("Not Found", 404)

@bp.route('/<int:groupid>', methods=['PUT'])
@json_body
def replace_group(groupid, data):
    """
    Replace Group Resource Representation

    Args:
        groupid: Path Parameter - Unique ID of Group Resource (int)
        request.body - JSON formatted Group Resource attributes

    Returns:
        Confirmation or Error Message
    """
    group = Group.retrieve(groupid)
    if not group:
        return make_response('Not found', 404)

    try:
        new_group_data = group_schema.load(data)
        group.update(**new_group_data)
    except Exception as e:
        current_app.logger.warning(
            f'replace_group(groupid={groupid}) failed.\nUpdate error: {e}'
            )
        return make_response('Bad request', 400)

    return make_response('OK', 200)

@bp.route('/<int:groupid>', methods=['PATCH'])
@json_body
def update_group(groupid, data):
    """
    Update Group Resource Representation

    Args:
        groupid: Path Parameter - Unique ID of Group Resource (int)
        request.body - JSON formatted Group Resource attributes

    Returns:
        Confirmation or Error Message
    """
    group = Group.retrieve(groupid)
    if not group:
        return make_response('Not found', 404)

    try:
        new_group_data = group_schema.load(data, partial=True)
        group.update(**new_group_data)
    except Exception as e:
        current_app.logger.warning(
            f'replace_group(groupid={groupid}) failed.\nUpdate error: {e}'
            )
        return make_response('Bad request', 400)

    return make_response('OK', 200)

@bp.route('/<int:groupid>', methods=['DELETE'])
def delete_group(groupid):
    """
    Delete Group Resource

    Args:
        groupid: Path Parameter - Unique ID of Group Resource (int)

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
def list_group_members(groupid):
    """
    Retrieve Group members

    Args:
        groupid: Path Parameter - Unique ID of Group Resource (int)
        request.args - Query String parameters: fields

    Returns:
        JSON array of User Resource Representations or Error Message
    """
    return "Retrieve Group members mock-up", 404

@bp.route('/<int:groupid>/members/<int:userid>', methods=['PUT'])
def add_user_to_group(groupid, userid):
    """
    Add User to Group

    Args:
        groupid: Path Parameter - Unique ID of Group Resource (int)
        userid: Path Parameter - Unique ID of User Resource (int)

    Returns:
        Confirmation or Error Message
    """
    return "Add User to Group mock-up", 200

@bp.route('/<int:groupid>/members/<int:userid>', methods=['DELETE'])
def delete_user_from_group(groupid, userid):
    """
    Delete User from Group

    Args:
        groupid: Path Parameter - Unique ID of Group Resource (int)
        userid: Path Parameter - Unique ID of User Resource (int)

    Returns:
        Confirmation or Error Message
    """
    return "Delete User from Group mock-up", 200
