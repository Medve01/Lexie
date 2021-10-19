import json
import os
import tinydb
import pytest

from lexie.app import create_app
from tests.fixtures.mock_lexieclasses import MockLexieDevice
from lexie.caching import flush_cache

MOCK_CALLED=""

@pytest.fixture
def app(monkeypatch):
    def mock_prepare_db():
        pass
    def mock_thread_start(self):
        pass
    monkeypatch.setattr('threading.Thread.start', mock_thread_start)
    monkeypatch.setattr('lexie.app.prepare_db', mock_prepare_db)
    _app = create_app(testing=True)
    _app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    _app.config['SQLALCHEMY_BINDS'] = {'events': 'sqlite://'}
    _app.config['ROUTINES_DB'] = '/tmp/routines_db.json'
    routines_db = tinydb.TinyDB(_app.config['ROUTINES_DB'])
    routines_db.truncate()
    routines_db.table('trigger').truncate()
    routines_db.table('event').truncate()
    routines_db.table('timer').truncate()
    flush_cache()
    import lexie.smarthome.models as models
    models.db.create_all()
    # set up test data
    rooms = models.Room.query.all()
    if len(rooms) == 0:
        room = models.Room(id='1234', name = 'Test room 1')
        models.db.session.add(room)
        room = models.Room(id='4321', name = 'Test room 2')
        models.db.session.add(room)
    devicetypes = models.DeviceType.query.all()
    if len(devicetypes) == 0:
        devicetype = models.DeviceType(id=1, name='Relay', actions=json.dumps([{"name": "onoff", "icon": "fa fa-toggle-on"}, {"name": "toggle", "icon": "fas fa-bullseye"}]))
        models.db.session.add(devicetype)
    devices = models.Device.query.all()
    if len(devices) == 0:
        device = models.Device(
            id='1234',
            name='Test Device',
            device_type=1,
            manufacturer='shelly',
            product='shelly1',
            attributes = json.dumps({'ip_address': '127.0.0.1'})
        )
        models.db.session.add(device)
        device = models.Device(
            id='4321',
            name='Test Device 2',
            device_type=1,
            manufacturer='shelly',
            product='shelly1',
            attributes = json.dumps({'ip_address': '127.0.0.2'})
        )
        models.db.session.add(device)
    models.db.session.commit()
    yield _app
    flush_cache
    return app

@pytest.fixture
def routines_db(app):
    with app.app_context():
        db = tinydb.TinyDB(app.config['ROUTINES_DB'])
        db.truncate()
        triggers = db.table('trigger')
        triggers.truncate()
        steps = db.table('step')
        steps.truncate()
    yield
    with app.app_context():
        db = tinydb.TinyDB(app.config['ROUTINES_DB'])
        db.truncate()
        triggers = db.table('trigger')
        triggers.truncate()
        steps = db.table('step')
        steps.truncate()

@pytest.fixture
def client(app):
    _client = app.test_client()
    return _client