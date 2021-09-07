import pytest
from lexie.app import create_app
from lexie.db import init__db
from lexie.devices.LexieDevice import LexieDevice, LexieDeviceType

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
        assert testdevice.device_type.name == 'Relay' # Test devicetype is always 1
        assert testdevice.device_name == 'Test device'

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
                "has_timer": False,
                "ison": True,
                "source": "http",
                "timer_duration": 0,
                "timer_remaining": 0,
                "timer_started": 0
            }
        ),
        (
            "off",
            {
                "has_timer": False,
                "ison": False,
                "source": "http",
                "timer_duration": 0,
                "timer_remaining": 0,
                "timer_started": 0
            }
        ),
        (
            "toggle",
            {
                "has_timer": False,
                "ison": False,
                "source": "http",
                "timer_duration": 0,
                "timer_remaining": 0,
                "timer_started": 0
            }
        ),
        (
            "status",
            {
                "has_timer": False,
                "ison": False,
                "source": "http",
                "timer_duration": 0,
                "timer_remaining": 0,
                "timer_started": 0
            }
        )
    ]
)
def test_device_relay_actions(monkeypatch,app, onoff, results):
    class MockHWDevice:
        def __init__(self) -> None:
            pass
        def relay_action_set(self, onoff):
            if onoff:
                return  {
                            "has_timer": False,
                            "ison": True,
                            "source": "http",
                            "timer_duration": 0,
                            "timer_remaining": 0,
                            "timer_started": 0
                        }
            return  {
                        "has_timer": False,
                        "ison": False,
                        "source": "http",
                        "timer_duration": 0,
                        "timer_remaining": 0,
                        "timer_started": 0
                    }
        def relay_action_toggle(self):
            return  {
                        "has_timer": False,
                        "ison": False,
                        "source": "http",
                        "timer_duration": 0,
                        "timer_remaining": 0,
                        "timer_started": 0
                    }
        def relay_property_get_status(self):
            return  {
                        "has_timer": False,
                        "ison": False,
                        "source": "http",
                        "timer_duration": 0,
                        "timer_remaining": 0,
                        "timer_started": 0
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
        elif onoff == "status":
            assert test_device.relay_property_get_status == results