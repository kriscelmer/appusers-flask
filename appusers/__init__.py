from flask import Flask
from appusers import users, groups, login, models, database, configuration


def create_app():
    """Initialize core application."""
    app = Flask(__name__, instance_relative_config=False)

    configuration.configure(app)

    with app.app_context():

        # Register Blueprints
        app.register_blueprint(users.bp)
        app.register_blueprint(groups.bp)
        app.register_blueprint(login.bp)

        # Initialize Marshmallow object from models
        models.ma.init_app(app)

        # Initialize Database object
        database.db.init_app(app)
        database.db.create_all()

        # Initialize JWT Manager
        login.jwt.init_app(app)

        return app
