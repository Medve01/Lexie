import pytest
from lexie.app import create_app
from lexie.db import init__db
from lexie.devices.device import LexieDevice

@pytest.fixture
def app():
    _app = create_app()
    with _app.app_context():
        init__db()
    return _app

def test_device_existing_device(app):
    with app.app_context():
        device_id = '1234'
        testdevice = LexieDevice(device_id)

    assert testdevice.device_id == device_id

def test_device_status_existing_device(app):
    with app.app_context():
        device_id='1234'
        testdevice = LexieDevice(device_id)
    status = testdevice.status()
    assert status['device_id'] == device_id
    assert (status['online'] is True) or (status['online'] is False)
    assert (status['ison'] is True) or (status['ison'] is False)
    assert status['device_type'] == 'test devicetype'
    assert status['device_name'] == 'Test device'

def test_device_nonexisting_device(app):
    with app.app_context():
        device_id = '12345'
        with pytest.raises(Exception):
            testdevice = LexieDevice(device_id)