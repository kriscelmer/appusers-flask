"""Group Resource Implementation module

This module declares a Flask Blueprint of Group Resources,
as well as all Operations related to:

    - Groups Collection
    - Group Document
    - Controllers associated with Group Resources

Blueprint is registered in Application Factory function.
"""

from flask import Blueprint, jsonify, make_response
from appusers.users import users_list


# Create Groups enpoint Blueprint
bp = Blueprint('groups', __name__, url_prefix='/groups')

# Initialize some data
groups_list = [{'id': 0,
                'groupname': 'admins',
                'description': 'Administrators'},
               {'id': 1,
                'groupname': 'friends',
                'description': 'Friends and Family'}]

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
    return jsonify(groups_list)

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
    response = make_response("Created", 201)
    response.headers['Location'] = '/groups/0'
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
    if 0 <= groupid and groupid <= len(groups_list):
        return jsonify(groups_list[groupid])
    else:
        return "Not Found", 404

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
    return "Replace Group Resource Representation mock-up", 200

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
    return "Update Group Resource Representation mock-up", 200

@bp.route('/<int:groupid>', methods=['DELETE'])
def delete_group(groupid):
    """
    Delete Group Resource

    Args:
        groupid: Path Parameter - Unique ID of Group Resource (int)

    Returns:
        Confirmation or Error Message
    """
    return "Delete Group Resource mock-up", 200

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
    if 0 <= groupid and groupid <= len(groups_list):
        return jsonify(users_list)
    else:
        return "Not Found", 404

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
