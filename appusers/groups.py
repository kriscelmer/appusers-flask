from flask import Blueprint, jsonify


# Create Groups enpoint Blueprint
bp = Blueprint('groups', __name__, url_prefix='/groups')

# Initialize some data
groups_list = [{'id': 0,
                'groupname': 'admins',
                'description': 'Administrators'},
               {'id': 1,
                'groupname': 'friends',
                'description': 'Friends and Family'}]

@bp.route('')
def list_groups():
    return jsonify(groups_list)
