"""Group Resource Implementation module

This module declares a Flask Blueprint of Group Resources,
as well as all Operations related to:

    - Groups Collection
    - Group Document
    - Controllers associated with Group Resources

Blueprint is registered in Application Factory function.
"""

from flask import Blueprint, request, jsonify, make_response, url_for
from appusers.database import Group
from appusers.schema import group_schema, group_list_schema


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
    list = Group.get_list({})
    return jsonify(group_list_schema.dump(list))

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
    if not request.is_json:
        return make_response('Unsupported Media Type', 415)

    try:
        data = request.get_json()
    except Exception as e:
        print(e)
        return make_response('Bad request', 400)

    new_group = Group(**data)
    response = make_response('Created', 201)
    response.headers['Location'] = url_for('groups.retrieve_group',
        groupid=new_group.groupid)

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
    group = Group.retrieve(groupid)
    if not group:
        return make_response('Not found', 404)

    if not request.is_json:
        return make_response('Unsupported Media Type', 415)

    try:
        data = request.get_json()
    except Exception as e:
        return make_response('Bad request', 400)

    group.update(**data)

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
    group = Group.retrieve(groupid)
    if not group:
        return make_response('Not found', 404)

    if not request.is_json:
        return make_response('Unsupported Media Type', 415)

    try:
        data = request.get_json()
    except Exception as e:
        return make_response('Bad request', 400)

    group.update(**data)

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
        group.remove()
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
