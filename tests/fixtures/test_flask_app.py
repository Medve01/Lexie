import json

import pytest

from lexie.app import create_app
from tests.fixtures.mock_lexieclasses import MockLexieDevice

MOCK_CALLED=""

@pytest.fixture
def app(monkeypatch):
    def mock_prepare_db():
        pass
    monkeypatch.setattr('lexie.app.prepare_db', mock_prepare_db)
    _app = create_app(testing=True)
    _app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    import lexie.smarthome.models as models
    models.db.create_all()
    # set up test data
    room = models.Room(id='1234', name = 'Test room 1')
    models.db.session.add(room)
    room = models.Room(id='4321', name = 'Test room 2')
    models.db.session.add(room)
    devicetype = models.DeviceType(id=1, name='Relay', actions=json.dumps([{"name": "onoff", "icon": "fa fa-toggle-on"}, {"name": "toggle", "icon": "fas fa-bullseye"}]))
    models.db.session.add(devicetype)
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
    return _app

@pytest.fixture
def client(app):
    _client = app.test_client()
    return _client