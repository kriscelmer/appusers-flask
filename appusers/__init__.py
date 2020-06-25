from flask import Flask
from appusers import users, groups, login


def create_app():
    """Initialize core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config['DEBUG'] = True
    app.config['ENV'] = 'development'

    with app.app_context():

        # Register Blueprints
        app.register_blueprint(users.bp)
        app.register_blueprint(groups.bp)
        app.register_blueprint(login.bp)

        return app
