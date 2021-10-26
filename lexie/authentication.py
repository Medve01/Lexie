import secrets

import bcrypt
import tinydb
from flask import current_app


class User:
    """represents the one and only user"""
    def is_active(self): # pylint: disable=no-self-use
        """True as there is only one user which is always active."""
        return True # pragma: nocover

    def get_id(self): # pylint: disable=no-self-use
        """Hardcoded, since we only have one user."""
        return 'admin' # pragma: nocover

    def is_authenticated(self): # pylint: disable=no-self-use
        """No clue what to do with this - yet."""
        return True # pragma: nocover

    def is_anonymous(self): # pylint: disable=no-self-use
        """False, as anonymous users aren't supported."""
        return False # pragma: nocover

def generate_apikey():
    """ Generates and stores a new API key.
        Existing API key will be overwritten"""
    apikey = secrets.token_hex(40)
    salt = bcrypt.gensalt()
    hashed_apikey = bcrypt.hashpw(apikey.encode('UTF-8'), salt)
    apikey_dict = {
        'id': 'apikey',
        'apikey': hashed_apikey.decode('UTF-8')
    }
    database = tinydb.TinyDB(current_app.config['ROUTINES_DB'])
    value = database.search(tinydb.Query().id == 'apikey')
    if value != []:
        database.remove(tinydb.Query().id == 'apikey')
    database.insert(apikey_dict)
    return apikey

def have_apikey():
    """ returns True if we have an API key hash stored, otherwise False """
    database = tinydb.TinyDB(current_app.config['ROUTINES_DB'])
    value = database.search(tinydb.Query().id == 'apikey')
    return value != []

def check_apikey(sent_api_key):
    """ to be called as before_request on API endpoints.
        checks authentication header or logon status and returns 403 if not ok"""
    database = tinydb.TinyDB(current_app.config['ROUTINES_DB'])
    result = database.search(tinydb.Query().id == 'apikey')
    if result == []:
        return False
    apikey_hash = result[0]['apikey']
    return bcrypt.checkpw(sent_api_key.encode('UTF-8'), apikey_hash.encode('UTF-8'))

def check_if_password_exists():
    """Checks if we have a passsword hash stored for UI authentication

    Returns:
        [bool]: [True if we have, False if not]
    """
    database = tinydb.TinyDB(current_app.config['ROUTINES_DB'])
    result = database.search(tinydb.Query().id == 'ui_password')
    if result == []:
        return False
    return True

def set_password(password):
    """Saves password in database

    Args:
        password ([str]): [the UI password]
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('UTF-8'), salt)
    password_dict = {
        'id': 'ui_password',
        'ui_password': hashed_password.decode('UTF-8')
    }

    database = tinydb.TinyDB(current_app.config['ROUTINES_DB'])
    result = database.search(tinydb.Query().id == 'ui_password')
    if result != []:
        database.remove(tinydb.Query().id == 'ui_password')
    database.insert(password_dict)

def check_password(password):
    """[Checks password against stored hash]

    Args:
        password ([type]): [description]
    """
    database = tinydb.TinyDB(current_app.config['ROUTINES_DB'])
    result = database.search(tinydb.Query().id == 'ui_password')
    if result == []:
        return False # pragma: nocover
    password_hash = result[0]['ui_password']
    return bcrypt.checkpw(password.encode('UTF-8'), password_hash.encode('UTF-8'))
