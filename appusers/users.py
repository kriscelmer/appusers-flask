from flask import Blueprint, jsonify


# Create Users enpoint Blueprint
bp = Blueprint('users', __name__, url_prefix='/users')

# Initialize some data
users_list = [{'id': 0,
               'username': 'johne',
               'firstname': 'John',
               'lastname': 'Example',
               'contactInfo': {
                    'email': 'johne@example.com',
                    'phone': '123.444.5555'
                    }
               },
               {'id': 1,
                'username': 'lindas',
                'firstname': 'Linda',
                'lastname': 'Someone',
                'contactInfo': {
                    'email': 'lindas@example.com',
                    'phone': '123.444.6666'
                }
               }]

@bp.route('')
def list_users():
    return jsonify(users_list)
