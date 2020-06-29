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
from appusers.models import Group, group_schema, group_list_schema


# Create Groups enpoint Blueprint
bp = Blueprint('groups', __name__, url_prefix='/groups')

# Initialize some data
admins = Group(
    groupid=0,
    groupname='admins',
    description='Administrators'
    )
friends = Group(
    groupid=1,
    groupname='friends',
    description='Friends and Family'
)

groups_list = {0: admins, 1: friends}
groups_max_index = 1

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
    filtered_list = groups_list.values()
    return jsonify(group_list_schema.dump(filtered_list))

@bp.route('', methods=['POST'])
def create_group():
    """
    Create Group Resource

    Args:
        request.body - JSON formatted Group Resource attributes

    Returns:
        Confirmation or Error Message
        'Location' Response Header
    """
    global groups_max_index

    if not request.is_json:
        return make_response('Unsupported Media Type', 415)

    try:
        data = request.get_json()
    except Exception as e:
        return make_response('Bad request', 400)

    try:
        new_group_data = group_schema.load(data)
    except ValidationError as e:
        current_app.logger.warning(
            f'create_group() failed.\nValidationError: {e}'
            )
        return make_response('Bad request', 400)

    groups_max_index = groups_max_index + 1
    new_group_data['groupid'] = groups_max_index
    groups_list[groups_max_index] = Group(**new_group_data)
    response = make_response('Created', 201)
    response.headers['Location'] = url_for('groups.retrieve_group', groupid=groups_max_index)

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
    if groupid in groups_list:
        return jsonify(group_schema.dump(groups_list[groupid]))
    else:
        return make_response('Not Found', 404)

@bp.route('/<int:groupid>', methods=['PUT'])
def replace_group(groupid):
    """
    Replace Group Resource Representation

    Args:
        groupid: Path Parameter - Unique ID of Group Resource (int)
        request.body - JSON formatted Group Resource attributes

    Returns:
        Confirmation or Error Message
    """
    if groupid not in groups_list:
        return make_response('Not found', 404)

    if not request.is_json:
        return make_response('Unsupported Media Type', 415)

    try:
        data = request.get_json()
    except Exception as e:
        return make_response('Bad request', 400)

    try:
        new_group_data = group_schema.load(data)
    except ValidationError as e:
        current_app.logger.warning(
            f'replace_group(groupid={groupid}) failed.\nValidationError: {e}'
            )
        return make_response('Bad request', 400)

    groups_list[groupid].update(**new_group_data)

    return make_response('OK', 200)

@bp.route('/<int:groupid>', methods=['PATCH'])
def update_group(groupid):
    """
    Update Group Resource Representation

    Args:
        groupid: Path Parameter - Unique ID of Group Resource (int)
        request.body - JSON formatted Group Resource attributes

    Returns:
        Confirmation or Error Message
    """
    if groupid not in groups_list:
        return make_response('Not found', 404)

    if not request.is_json:
        return make_response('Unsupported Media Type', 415)

    try:
        data = request.get_json()
    except Exception as e:
        return make_response('Bad request', 400)

    try:
        new_group_data = group_schema.load(data, partial=True)
    except ValidationError as e:
        current_app.logger.warning(
            f'update_group(groupid={groupid}) failed.\nValidationError: {e}'
            )
        return make_response('Bad request', 400)

    groups_list[groupid].update(**new_group_data)

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
    if groupid in groups_list:
        del(groups_list[groupid])
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
