import pytest
import tinydb

from lexie import apikey
from tests.fixtures.test_flask_app import app

def test_have_apikey(app):
    with app.app_context():
        database = tinydb.TinyDB(app.config['ROUTINES_DB'])
        result = database.search(tinydb.Query().id == 'apikey')
        if result != []:
            database.remove(tinydb.Query().id == 'apikey')
        assert apikey.have_apikey() is False
        database.insert({'id': 'apikey', 'apikey': 'asdfasdfasdf'})
        assert apikey.have_apikey() is True
        database.remove(tinydb.Query().id == 'apikey')

def test_generate_apikey(app):
    with app.app_context():
        database = tinydb.TinyDB(app.config['ROUTINES_DB'])
        result = database.search(tinydb.Query().id == 'apikey')
        if result != []:
            database.remove(tinydb.Query().id == 'apikey')
        api_key = apikey.generate_apikey()
        database = tinydb.TinyDB(app.config['ROUTINES_DB'])
        result = database.search(tinydb.Query().id == 'apikey')
        api_key_hash = result[0]['apikey']
        assert result != [] and result is not None
        api_key = apikey.generate_apikey()
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
        api_key = apikey.generate_apikey()
        assert apikey.check_apikey('nyenyere') is False
        assert apikey.check_apikey(api_key) is True
        database.remove(tinydb.Query().id == 'apikey')
        assert apikey.check_apikey(api_key) is False
