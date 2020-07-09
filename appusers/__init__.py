from flask import Flask
from datetime import timedelta
from appusers import users, groups, login, models, database


def create_app():
    """Initialize core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config['DEBUG'] = True
    app.config['ENV'] = 'development'
    # SERVER_NAME config variable required for hypermedia links generation
    app.config['SERVER_NAME'] = 'localhost:5000'
    # SQLAlchemy configuration for development, uses SQLite3 local fiele DB
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///appusers.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # X-API-Key value for development
    app.config['API_KEY'] = 'appusers' # change this!
    # Flask-JWT-Extended configuration for development
    app.config['JWT_SECRET_KEY'] = 'super-secret' # change this!
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
        days=1,
        hours=0,
        minutes=0,
        seconds=0
        )
    # Login parameters related to User account lock for development
    app.config['MAX_FAILED_LOGIN_ATTEMPTS'] = 5
    app.config['LOCK_TIMEOUT'] = timedelta(
        days=0,
        hours=0,
        minutes=5,
        seconds=0
        )

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
