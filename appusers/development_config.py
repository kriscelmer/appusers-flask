"""Application settings used in development"""

from datetime import timedelta

# SERVER_NAME config variable required for hypermedia links generation
SERVER_NAME = 'localhost:5000'

# SQLAlchemy configuration for development, uses SQLite3 local file DB
SQLALCHEMY_DATABASE_URI = 'sqlite:///appusers.sqlite3'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# X-API-Key value for development
API_KEY = 'appusers' # change this!

# Flask-JWT-Extended configuration for development
JWT_SECRET_KEY = 'super-secret' # change this!
JWT_ACCESS_TOKEN_EXPIRES = timedelta(
    days=1,
    hours=0,
    minutes=0,
    seconds=0
    )
    
# Login parameters related to User account lock for development
MAX_FAILED_LOGIN_ATTEMPTS = 5
LOCK_TIMEOUT = timedelta(
    days=0,
    hours=0,
    minutes=5,
    seconds=0
    )
