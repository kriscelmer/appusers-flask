from flask import Flask
from appusers import users, groups, login, models, database


def create_app():
    """Initialize core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config['DEBUG'] = True
    app.config['ENV'] = 'development'
    # SERVER_NAME config variable required for hypermedia links generation
    app.config['SERVER_NAME'] = 'localhost:5000'
    # SQLAlchemy configuration for development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///appusers.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

        return app
