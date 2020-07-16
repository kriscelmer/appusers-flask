"""Application Configration Module

Application Configuration variables are available to all modules
through app.config (or current_app.config) dictionary.
This module declares configure(app) function, which is called from
Application Factory.
"""
import os, argparse, ast
from datetime import timedelta
from appusers.models import config_variables_schema

def configure(app):
    """Initialize Flask app.config

    Order of setting of configuration variables:
        1) required configration variables are hard-coded in this function
        2) configuration file with Python syntax
        3) environment variables
        4) command line options
    """

    # Set hard-coded values

    app.config['DEBUG'] = True
    app.config['ENV'] = 'development'

    # SERVER_NAME config variable required for hypermedia links generation
    app.config['SERVER_NAME'] = 'localhost:5000'

    # SQLAlchemy configuration for development, uses SQLite3 local file DB
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

    """ Read Configuration Variables from Python source file pointed by
        APPUSERS_CONFIG environment variable or from
        development_config.py (if env var not set)
        Relative path is resolved in Application root folder
    """

    if 'APPUSERS_CONFIG' in os.environ:
        py_file_name = os.environ['APPUSERS_CONFIG']
    else:
        # file name is relative to directory holding __init__.py module
        py_file_name = 'development_config.py'

    py_file_full_path = os.path.join(app.root_path, py_file_name)

    if os.path.isfile(py_file_full_path):
        app.logger.info(f'Reading app config from {py_file_name}')
        app.config.from_pyfile(py_file_full_path)
    else:
        app.logger.info(f'Configuration file {py_file_name} not found!')
        print(f'Configuration file {py_file_name} not found!')
        # exit(1)

    """ Read Configuration Variables from Environment Variables
        by loading dictionary from os.environ with
        models.config_variables_schema.

        Following Environment Variables are mapped to Config Variables:
        APPUSERS_DEBUG -> DEBUG
        APPUSERS_ENV -> ENV
        APPUSERS_SERVER_NAME -> SERVER_NAME
        APPUSERS_APPLICATION_ROOT -> APPLICATION_ROOT
        APPUSERS_DATABASE_URI -> SQLALCHEMY_DATABASE_URI
        APPUSERS_API_KEY -> API_KEY
        APPUSERS_SECRET_KEY -> JWT_SECRET_KEY
        APPUSERS_ACCESS_TOKEN_EXPIRES -> JWT_ACCESS_TOKEN_EXPIRES
        APPUSERS_MAX_FAILED_LOGIN_ATTEMPTS -> MAX_FAILED_LOGIN_ATTEMPTS
        APPUSERS_LOCK_TIMEOUT -> LOCK_TIMEOUT
    """
    try:
        envvar_config = config_variables_schema.load(os.environ, partial=True)
        app.logger.info(f'Config from Environment Variables:\n{envvar_config}')
        app.config.from_mapping(envvar_config)
    except Exception as e:
        app.logger.warning(f'Environment Variables errors:\n{e}')
        app.logger.warning('Skipping all Environment Variables!')
        # exit(1)

    """ Read Configuration Variables from Command Line.
        Map command line options to environment variables and validate with
        models.config_variables_schema.
    """
    parser = argparse.ArgumentParser(
        description='Application Users RESTful API Server')
    parser.add_argument('--debug', nargs='?', type=ast.literal_eval,
        metavar='True|False', help='Flask DEBUG config value',
        dest='APPUSERS_DEBUG')
    parser.add_argument('--env', nargs='?', type=str,
        metavar='development|production|...', help='Flask ENV config value',
        dest='APPUSERS_ENV')
    parser.add_argument('-s', '--server', nargs='?', type=str,
        metavar='hostname[:port]', help='Flask SERVER_NAME config value',
        dest='APPUSERS_SERVER_NAME')
    parser.add_argument('-r', '--app-root', nargs='?', type=str,
        metavar='/v2|...]', help='Flask APPLICATION_ROOT config value',
        dest='APPUSERS_APPLICATION_ROOT')
    parser.add_argument('-d', '--db-uri', nargs='?', type=str, metavar='URI',
        help='SQLAlchemy Database URI', dest='APPUSERS_DATABASE_URI')
    parser.add_argument('--api-key', nargs='?', type=str, metavar='STRING',
        help='X-API-Key Reaquest header value', dest='APPUSERS_API_KEY')
    parser.add_argument('--secret-key', nargs='?', type=str, metavar='STRING',
        help='JWT Secret Key', dest='APPUSERS_SECRET_KEY')
    parser.add_argument('-e', '--token-expires', nargs='?', type=int,
        metavar='INT', help='JWT Token expiration in seconds',
        dest='APPUSERS_ACCESS_TOKEN_EXPIRES')
    parser.add_argument('-f', '--failed-logins', nargs='?', type=int,
        metavar='INT',
        help='Maximum number of failed login attempts before account is locked',
        dest='APPUSERS_MAX_FAILED_LOGIN_ATTEMPTS')
    parser.add_argument('-l', '--lock-timeout', nargs='?', type=int,
        metavar='INT', help='Account lock timeout in seconds',
        dest='APPUSERS_LOCK_TIMEOUT')

    parsed_args, unknown = parser.parse_known_args()
    parsed_args = vars(parsed_args) # convert Namespace to dict
    cl_args = {k:v for k,v in parsed_args.items() if v is not None} # skip None items

    try:
        cl_args_config = config_variables_schema.load(cl_args, partial=True)
        app.logger.info(f'Config from Command Line options:\n{cl_args_config}')
        app.config.from_mapping(cl_args_config)
    except Exception as e:
        app.logger.warning(f'Command Line options errors:\n{e}')
        app.logger.warning('Skipping all Coommand Line options!')
        # exit(1)
