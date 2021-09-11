import pytest
from lexie.lexie_app import create_app
from lexie.db import init__db
from lexie.devices.LexieDevice import LexieDevice, LexieDeviceType, get_all_devices

class MockHWDevice:
    def __init__(self) -> None:
        pass
    def relay_action_set(self, onoff):
        if onoff:
            return  {
                        "ison": True,
                        "online": True
                    }
        return  {
                    "ison": False,
                    "online": True
                }
    def relay_action_toggle(self):
        return  {
                    "ison": False,
                    "online": True
                }
    def relay_property_get_status(self):
        return  {
                    "ison": False,
                    "online": True
                }
def mock_relay_action_set(self, onoff):
    mockhwdevice = MockHWDevice()
    return mockhwdevice.relay_action_set(onoff)
def mock_relay_action_toggle(self):
    mockhwdevice = MockHWDevice()
    return mockhwdevice.relay_action_toggle()
def mock_relay_property_get_status(self):
    mockhwdevice = MockHWDevice()
    return mockhwdevice.relay_action_toggle()

@pytest.fixture
def app():
    _app = create_app(testing=True)
    with _app.app_context():
        init__db()
    return _app

def test_device_existing_device(app):
    with app.app_context():
        device_id = '1234'
        testdevice = LexieDevice(device_id)

    assert testdevice.device_id == device_id
    assert testdevice.device_type.name == 'Relay' # Test devicetype is always 1
    assert testdevice.device_name == 'Test device'

def test_device_relay_status_existing_device(monkeypatch, app):
    with app.app_context():
        device_id='1234'
        testdevice = LexieDevice(device_id)
        monkeypatch.setattr('lexie.drivers.shelly.shelly1.HWDevice.relay_property_get_status', mock_relay_property_get_status)
        assert testdevice.relay_property_get_status(use_cache=False) == {
            "ison": False,
            "online": True,
            'lexie_source': "device"
        }
        assert testdevice.online is True


def test_device_relay_status_existing_device_from_cache(monkeypatch, app):
    with app.app_context():
        device_id='1234'
        testdevice = LexieDevice(device_id)
        monkeypatch.setattr('lexie.drivers.shelly.shelly1.HWDevice.relay_property_get_status', mock_relay_property_get_status)
        status = testdevice.relay_property_get_status(use_cache=False) # calling once so LexieDevice stores in cache
        assert testdevice.relay_property_get_status() == { # second time it should come from cache
            "ison": False,
            "online": True,
            'lexie_source': "cache"
        }

def test_device_nonexisting_device(app):
    with app.app_context():
        device_id = '12345'
        with pytest.raises(Exception):
            testdevice = LexieDevice(device_id)

def test_device_new(app):
    with app.app_context():
        attributes = {"ip_address": "127.0.0.1"}
        test_device = LexieDevice.new(device_name='Test device', device_type=LexieDeviceType(1), device_manufacturer='shelly', device_product='shelly1', device_attributes=attributes)
        assert test_device.device_name == 'Test device' and test_device.device_type.name == 'Relay'

@pytest.mark.parametrize(
    ("onoff", "results"),
    [
        (
            "on",
            {
                "ison": True,
                "online": True,
                "lexie_source": "device"
            }
        ),
        (
            "off",
            {
                "ison": False,
                "online": True,
                "lexie_source": "device"
            }
        ),
        (
            "toggle",
            {
                "ison": False,
                "online": True,
                "lexie_source": "device"
            }
        ),
    ]
)
def test_device_relay_actions(monkeypatch,app, onoff, results):
    monkeypatch.setattr('lexie.drivers.shelly.shelly1.HWDevice.relay_action_set', mock_relay_action_set)
    monkeypatch.setattr('lexie.drivers.shelly.shelly1.HWDevice.relay_action_toggle', mock_relay_action_toggle)
    monkeypatch.setattr('lexie.drivers.shelly.shelly1.HWDevice.relay_property_get_status', mock_relay_property_get_status)
    with app.app_context():
        test_device = LexieDevice('1234')
        test_device.relay_action_set(True)
        if onoff == "on":
            assert test_device.relay_action_set(True) == results
        elif onoff == "off":
            assert test_device.relay_action_set(False) == results
        elif onoff == "toggle":
            assert test_device.relay_action_toggle() == results

def test_get_all_devices(app):
    with app.app_context():
        test_devices = get_all_devices()
        assert len(test_devices) == 2
        for test_device in test_devices:
            assert isinstance(test_device, LexieDevice)
