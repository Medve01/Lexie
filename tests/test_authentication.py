import pytest
import tinydb

from lexie import authentication
from tests.fixtures.test_flask_app import app

def test_have_apikey(app):
    with app.app_context():
        database = tinydb.TinyDB(app.config['ROUTINES_DB'])
        result = database.search(tinydb.Query().id == 'apikey')
        if result != []:
            database.remove(tinydb.Query().id == 'apikey')
        assert authentication.have_apikey() is False
        database.insert({'id': 'apikey', 'apikey': 'asdfasdfasdf'})
        assert authentication.have_apikey() is True
        database.remove(tinydb.Query().id == 'apikey')

def test_generate_apikey(app):
    with app.app_context():
        database = tinydb.TinyDB(app.config['ROUTINES_DB'])
        result = database.search(tinydb.Query().id == 'apikey')
        if result != []:
            database.remove(tinydb.Query().id == 'apikey')
        api_key = authentication.generate_apikey()
        database = tinydb.TinyDB(app.config['ROUTINES_DB'])
        result = database.search(tinydb.Query().id == 'apikey')
        api_key_hash = result[0]['apikey']
        assert result != [] and result is not None
        api_key = authentication.generate_apikey()
        database = tinydb.TinyDB(app.config['ROUTINES_DB'])
        result = database.search(tinydb.Query().id == 'apikey')
        assert result[0]['apikey'] != api_key_hash
        database.remove(tinydb.Query().id == 'apikey')

def test_check_apikey(app):
    with app.app_context():
        database = tinydb.TinyDB(app.config['ROUTINES_DB'])
        result = database.search(tinydb.Query().id == 'apikey')
        if result != []:
            database.remove(tinydb.Query().id == 'apikey')
        api_key = authentication.generate_apikey()
        assert authentication.check_apikey('nyenyere') is False
        assert authentication.check_apikey(api_key) is True
        database.remove(tinydb.Query().id == 'apikey')
        assert authentication.check_apikey(api_key) is False

def test_check_if_password_exists(app):
    with app.app_context():
        database = tinydb.TinyDB(app.config['ROUTINES_DB'])
        result = database.search(tinydb.Query().id=='ui_password')
        if result != []:
            database.remove(tinydb.Query().id == 'ui_password')
        assert authentication.check_if_password_exists() == False
        database.insert({
            'id': 'ui_password',
            'ui_password': 'lófütty'
        })
        assert authentication.check_if_password_exists() == True

def test_check_password(app):
    with app.app_context():
        authentication.set_password('password')
        assert authentication.check_password('password') is True
        assert authentication.check_password('password.') is False