from flask import Flask
from appusers import users, groups


def create_app():
    """Initialize core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config['DEBUG'] = True
    app.config['ENV'] = 'development'

    with app.app_context():

        # Register Blueprints
        app.register_blueprint(users.bp)
        app.register_blueprint(groups.bp)

        return app
