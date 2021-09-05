import pytest
from lexie.app import create_app
from lexie.db import init__db
from lexie.devices.device import LexieDevice, LexieDeviceType

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
        assert testdevice.device_id == device_id
        assert testdevice.online is True or testdevice.online is False
        assert testdevice.ison is True or testdevice.ison is False
        assert testdevice.device_type.name == 'Test devicetype' # Test devicetype is always 1
        assert testdevice.device_name == 'Test device'

def test_device_nonexisting_device(app):
    with app.app_context():
        device_id = '12345'
        with pytest.raises(Exception):
            testdevice = LexieDevice(device_id)

def test_device_new(app):
    with app.app_context():
        test_device = LexieDevice.new(device_name='Test device', device_type=LexieDeviceType(1))
        assert test_device.device_name == 'Test device' and test_device.device_type.name == 'Test devicetype' # Test devicetype is always 1