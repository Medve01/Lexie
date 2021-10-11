import json

import pytest

# from lexie.db import init__db
from lexie.smarthome.LexieDevice import (LexieDevice, LexieDeviceType,
                                         get_all_devices, get_all_devices_with_rooms)
from lexie.smarthome.exceptions import NotFoundException
from lexie.smarthome.Room import Room
from tests.fixtures.test_flask_app import app
from tests.fixtures.mock_lexieclasses import device_data

MOCK_CALL = {}

class MockHWDevice:
    def __init__(self, device_data) -> None:
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
        self.device_ip = '192.168.100.37'
        self.supports_events = True

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
    mockhwdevice = MockHWDevice(device_data)
    return mockhwdevice.action_turn(onoff)
def mock_action_toggle(self):
    mockhwdevice = MockHWDevice(device_data)
    return mockhwdevice.action_toggle()
def mock_get_status(self):
    mockhwdevice = MockHWDevice(device_data)
    return mockhwdevice.get_status()


def test_device_existing_device(monkeypatch, app):
    def mock_hw_device_supports_events(self):
        return True
    monkeypatch.setattr('lexie.drivers.shelly.shelly1.HWDevice.get_status', mock_get_status)
    monkeypatch.setattr('lexie.drivers.shelly.shelly1.HWDevice.__init__', MockHWDevice.__init__)

    with app.app_context():
        device_id = '1234'
        testdevice = LexieDevice(device_id)
        testtype = LexieDeviceType(1)

    assert testdevice.device_id == device_id
    assert testdevice.device_type.name == 'Relay'
    assert testdevice.device_name == 'Test Device'
    result = testdevice.to_dict()
    # TODO: MOCK HWDEVICE!!!!!!!
    assert result == {
        'device_id': '1234',
        'device_name': 'Test Device',
        'device_type': testtype.to_dict(),
        'device_manufacturer': 'shelly',
        'device_product': 'shelly1',
        'device_attributes': {
            'ip_address': '127.0.0.1'
        },
        'device_ison': False,
        'device_online': True,
        'supports_events': True,
        'room': {'room_id': None, 'room_name': 'Unassigned'}
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
        assert testdevice.get_status()['lexie_source'] == 'cache'

def test_device_nonexisting_device(app):
    with app.app_context():
        device_id = '12345'
        with pytest.raises(NotFoundException):
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


def test_get_all_devices_with_rooms(app):
    with app.app_context():
        test_devices = get_all_devices_with_rooms()
    assert test_devices == [
        {'room_name': 'Test room 1', 'room_devices': [], 'room_id': '1234', 'room_visible': True},
        {'room_name': 'Test room 2', 'room_devices': [], 'room_id': '4321', 'room_visible': True},
        {'room_name': 'Unassigned', 'room_id': None, 'room_visible': False, 'room_devices': [
            {
                'device_id': '1234',
                'device_name': 'Test Device',
                'device_type': {'devicetype_id': 1, 'devicetype_name': 'Relay'},
                'device_manufacturer': 'shelly',
                'device_product': 'shelly1',
                'device_attributes': {'ip_address': '127.0.0.1'},
                'device_ison': None,
                'device_online': False,
                'supports_events': True,
                'room': {'room_id': None, 'room_name': 'Unassigned'}
            },
            {
                'device_id': '4321',
                'device_name': 'Test Device 2',
                'device_type': {'devicetype_id': 1, 'devicetype_name': 'Relay'},
                'device_manufacturer': 'shelly',
                'device_product': 'shelly1',
                'device_attributes': {'ip_address': '127.0.0.2'},
                'device_ison': None,
                'device_online': False,
                'supports_events': True,
                'room': {'room_id': None, 'room_name': 'Unassigned'}
            }
        ]}
    ]

def test_device_move(app):
    with app.app_context():
        device = LexieDevice('1234')
        if device.room is None:
            target = Room('1234')
        elif device.room.id == '1234':
            target = Room('1235')
        else:
            target = Room('1234')
        device.move(target)
        device = LexieDevice('1234')
        assert device.room.id == target.id

def test_device_supports_events(app):
    with app.app_context():
        device = LexieDevice('1234')
        # 1234 is a shelly device, which does suppport events
        assert device.supports_events == True

def test_device_setup_events(monkeypatch, app):
    def mock_hw_device_setup_events(self):
        return True
    monkeypatch.setattr('lexie.drivers.shelly.shelly1.HWDevice.setup_events', mock_hw_device_setup_events)
    with app.app_context():
        device = LexieDevice('1234')
        assert device.setup_events() is True

@pytest.mark.parametrize(
    ('cache', 'result'),
    [
        (
            'hit',
            {
                'key': '1234_status',
                'value': {'some': 'value', 'test': 'test_value'}
            }
        ),
        (
            'miss',
            {}
        ),
    ]

)
def test_device_set_status(monkeypatch, app, cache, result):
    def mock_get_value_from_cache(key):
        if cache == 'hit':
            return {'some': 'value'}
        elif cache == 'miss':
            return None
        else:
            raise Exception('screwed up parametrizing')

    
    def mock_set_value_in_cache(key, value):
        global MOCK_CALL
        MOCK_CALL = {
            'key': key,
            'value': value
        }
        return
    
    def mock_get_status(self):
        return {
            'online': True,
            'ison': False
        }

    global MOCK_CALL
    MOCK_CALL = {}
    # monkeypatch.setattr('lexie.caching.get_value_from_cache', mock_get_value_from_cache)
    monkeypatch.setattr('lexie.smarthome.LexieDevice.get_value_from_cache', mock_get_value_from_cache)
    # monkeypatch.setattr('lexie.caching.set_value_in_cache', mock_set_value_in_cache)
    monkeypatch.setattr('lexie.smarthome.LexieDevice.set_value_in_cache', mock_set_value_in_cache)
    monkeypatch.setattr('lexie.drivers.shelly.shelly1.HWDevice.__init__', MockHWDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.get_status', mock_get_status)
    with app.app_context():
        testdevice = LexieDevice(device_id='1234')
        testdevice.set_status('test', 'test_value')
    assert MOCK_CALL == result

def test_device_delete(monkeypatch, app):
    with app.app_context():
        testdevice = LexieDevice.new(
            device_name='Test device to be deleted',
            device_type=LexieDeviceType(1),
            device_product="shelly1",
            device_manufacturer='shelly',
            device_attributes={'ip_address': '127.0.0.1'}
        )
        test_id = testdevice.device_id
        testdevice.delete()
        with pytest.raises(NotFoundException):
            testdevice = LexieDevice(device_id=test_id)