import pytest
from lexie.app import create_app
from lexie.db import init__db
from lexie.smarthome.LexieDevice import LexieDevice, LexieDeviceType, get_all_devices

class MockHWDevice:
    def __init__(self) -> None:
        self.device_id= '1234'
        self.device_name= 'Bedroom light'
        # self.device_type: testtype.to_dict(),
        self.device_manufacturer= 'shelly'
        self.device_product= 'shelly1'
        self.device_attributes= {
            'ip_address': '192.168.100.37'
        }
        self.ison= None
        self.online= False

    def action_turn(self, onoff):
        if onoff:
            return  {
                        "ison": True,
                        "online": True
                    }
        return  {
                    "ison": False,
                    "online": True
                }
    def action_toggle(self):
        return  {
                    "ison": False,
                    "online": True
                }
    def get_status(self):
        return  {
                    "ison": False,
                    "online": True
                }
def mock_action_turn(self, onoff):
    mockhwdevice = MockHWDevice()
    return mockhwdevice.action_turn(onoff)
def mock_action_toggle(self):
    mockhwdevice = MockHWDevice()
    return mockhwdevice.action_toggle()
def mock_get_status(self):
    mockhwdevice = MockHWDevice()
    return mockhwdevice.get_status()

@pytest.fixture
def app():
    _app = create_app(testing=True)
    with _app.app_context():
        init__db()
    return _app

def test_device_existing_device(monkeypatch, app):
    monkeypatch.setattr('lexie.drivers.shelly.shelly1.HWDevice.get_status', mock_get_status)
    with app.app_context():
        device_id = '1234'
        testdevice = LexieDevice(device_id)
        testtype = LexieDeviceType(1)

    assert testdevice.device_id == device_id
    assert testdevice.device_type.name == 'Relay' # Test devicetype is always 1
    assert testdevice.device_name == 'Bedroom light'
    result = testdevice.to_dict()
    # TODO: MOCK HWDEVICE!!!!!!!
    assert result == {
        'device_id': '1234',
        'device_name': 'Bedroom light',
        'device_type': testtype.to_dict(),
        'device_manufacturer': 'shelly',
        'device_product': 'shelly1',
        'device_attributes': {
            'ip_address': '192.168.100.37'
        },
        'device_ison': False,
        'device_online': True
    }

def test_device_relay_status_existing_device(monkeypatch, app):
    with app.app_context():
        device_id='1234'
        testdevice = LexieDevice(device_id)
        monkeypatch.setattr('lexie.drivers.shelly.shelly1.HWDevice.get_status', mock_get_status)
        assert testdevice.get_status(use_cache=False) == {
            "ison": False,
            "online": True,
            'lexie_source': "device"
        }
        assert testdevice.online is True


def test_device_relay_status_existing_device_from_cache(monkeypatch, app):
    with app.app_context():
        device_id='1234'
        testdevice = LexieDevice(device_id)
        monkeypatch.setattr('lexie.drivers.shelly.shelly1.HWDevice.get_status', mock_get_status)
        status = testdevice.get_status(use_cache=False) # calling once so LexieDevice stores in cache
        assert testdevice.get_status() == { # second time it should come from cache
            "ison": False,
            "online": True,
            'lexie_source': "cache"
        }

def test_device_nonexisting_device(app):
    with app.app_context():
        device_id = '12345'
        with pytest.raises(Exception):
            LexieDevice(device_id)

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
    monkeypatch.setattr('lexie.drivers.shelly.shelly1.HWDevice.action_turn', mock_action_turn)
    monkeypatch.setattr('lexie.drivers.shelly.shelly1.HWDevice.action_toggle', mock_action_toggle)
    monkeypatch.setattr('lexie.drivers.shelly.shelly1.HWDevice.get_status', mock_get_status)
    with app.app_context():
        test_device = LexieDevice('1234')
        test_device.action_turn(True)
        if onoff == "on":
            assert test_device.action_turn(True) == results
        elif onoff == "off":
            assert test_device.action_turn(False) == results
        elif onoff == "toggle":
            assert test_device.action_toggle() == results

def test_get_all_devices(app):
    with app.app_context():
        test_devices = get_all_devices()
        assert len(test_devices) == 2
        for test_device in test_devices:
            assert isinstance(test_device, LexieDevice)
