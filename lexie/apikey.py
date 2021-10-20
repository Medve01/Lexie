import secrets

import bcrypt
import tinydb
from flask import current_app


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
