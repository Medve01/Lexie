import json
from typing import Any

import pytest

from lexie.smarthome.lexiedevice import LexieDevice, LexieDeviceType
from lexie.smarthome import exceptions
from tests.fixtures.test_flask_app import app, client
from tests.fixtures.mock_lexieclasses import MockLexieDevice
from tests.fixtures.mock_lexieclasses import device_data


def test_api_get_device(monkeypatch, client):
    """" tests /api/device/device_id"""
    def mocklexiedevice_init(Any, device_id):
        return MockLexieDevice(device_id)
    
    def mocklexiedevice_to_dict(Any):
        mock_device = MockLexieDevice('1234')
        return mock_device.to_dict()
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.to_dict', mocklexiedevice_to_dict)
    res = client.get('/api/device/1234')

    assert json.loads(res.data) == {
        "device_attributes":
            {
                "ip_address":"127.0.0.1"
            },
            "device_id":"1234",
            "device_manufacturer":"shelly",
            "device_name":"Mock device",
            "device_product":"shelly1",
            "device_type":
                {
                    "devicetype_id":1,
                    "devicetype_name":"Relay"
                },
            "device_ison": "ON",
            "device_online": "ONLINE"
        }

def test_api_get_device_nonexisting(monkeypatch, client):
    """" tests /api/device/device_id"""
    def mocklexiedevice_init(Any, device_id):
        raise exceptions.NotFoundException
    
    def mocklexiedevice_to_dict(Any):
        mock_device = MockLexieDevice('1234')
        return mock_device.to_dict()
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.__init__', mocklexiedevice_init)
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.to_dict', mocklexiedevice_to_dict)
    res = client.get('/api/device/1234')
    assert res.status_code == 404

@pytest.mark.parametrize(
    ("onoff","results"),
    (
        ("on", {"ison":True,"online": True, "lexie_source": "device"}),
        ("off", {"ison":False,"online": True, "lexie_source": "device"}),
        ("toggle", {"ison":False,"online": True, "lexie_source": "device"}),
        ("blarghfteh", {"Error:":"Invalid command"})
    )
)
def test_api_device_relay_actions(monkeypatch, client, onoff, results): #pylint: disable=redefined-outer-name
    """ tests /api/device/1234/on off toggle"""

    def mock_action_turn(Any, onoff):
        mock_device = MockLexieDevice('1234')
        return mock_device.action_turn(onoff)
    def mock_action_toggle(Any):
        mock_device = MockLexieDevice('1234')
        return mock_device.action_toggle()


    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.action_turn', mock_action_turn)
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.action_toggle', mock_action_toggle)
    res = client.get('/api/device/1234/' + onoff)
    assert json.loads(res.data) == results

def test_api_device_relay_actions_nonexisting_device(monkeypatch, client): #pylint: disable=redefined-outer-name
    """ tests /api/device/1234/on off toggle"""

    def mock_action_turn(Any, onoff):
        mock_device = MockLexieDevice('1234')
        return mock_device.action_turn(onoff)
    def mock_action_toggle(Any):
        mock_device = MockLexieDevice('1234')
        return mock_device.action_toggle()
    def mocklexiedevice_init(Any, device_id):
        raise exceptions.NotFoundException

    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.__init__', mocklexiedevice_init)
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.action_turn', mock_action_turn)
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.action_toggle', mock_action_toggle)
    res = client.get('/api/device/1234/toggle')
    assert res.status_code == 404

def test_api_new_device(monkeypatch, client):
    """ tests PUT /api/device """
    def new_lexiedevice(
        device_name: str, # pylint: disable=unused-argument
        device_type: LexieDeviceType, # pylint: disable=unused-argument
        device_product: str, # pylint: disable=unused-argument
        device_manufacturer: str, # pylint: disable=unused-argument
        device_attributes: Any # pylint: disable=unused-argument
    ):
        return MockLexieDevice(device_id='12345')

    # def new_lexiedevice_to_dict():
    #     return {
    #         "device_name": device_data['device_name'],
    #         "device_type": device_data['device_type'],
    #         "device_product": device_data['device_product'],
    #         "device_manufacturer": device_data['device_manufacturer'],
    #         "device_attributes": device_data['device_attributes']
    #     }

    # def mock_lexiedevice_init(device_id):
    #     return MockLexieDevice(device_id=device_id)
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.new', new_lexiedevice)
    # monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.__init__', mock_lexiedevice_init)
    res = client.put('/api/device/', data=json.dumps(device_data))
    assert json.loads(res.data) == {
                                        "device_attributes": {
                                                                "ip_address":"127.0.0.1"
                                                            },
                                        "device_name": "Mock device",
                                        "device_online": "ONLINE",
                                        "device_ison": "ON",
                                        "device_id":"12345",
                                        "device_manufacturer":"shelly",
                                        "device_product":"shelly1",
                                        "device_type": {
                                                            "devicetype_id":1,
                                                            "devicetype_name":"Relay"
                                                        }
                                    }

def test_api_get_all_devices(monkeypatch, client):
    def mock_get_all_devices():
        all_devices = []
        all_devices.append(MockLexieDevice('1234'))
        all_devices.append(MockLexieDevice('4321'))
        return all_devices
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.lexiedevice.get_all_devices', mock_get_all_devices)
    res = client.get('/api/device/')
    assert json.loads(res.data) == [
        {'device_attributes': {'ip_address': '127.0.0.1'},
        'device_id': '1234',
        'device_manufacturer': 'shelly',
        'device_name': 'Mock device',
        'device_product': 'shelly1',
        'device_type': {'devicetype_id': 1,
            'devicetype_name': 'Relay'},
        'room': {'room_id': '1234',
            'room_name': 'Test room 1'}},
        {'device_attributes': {'ip_address': '127.0.0.1'},
        'device_id': '4321',
        'device_manufacturer': 'shelly',
        'device_name': 'Mock device',
        'device_product': 'shelly1',
        'device_type': {'devicetype_id': 1,
        'devicetype_name': 'Relay'},
        'room': {'room_id': '1234',
            'room_name': 'Test room 1'}},
    ]

def test_api_get_all_devices_with_rooms(monkeypatch, client):
    def mock_get_all_devices_with_rooms():
        all_devices = [
            {'room_name': 'Bedroom', 'room_devices':[]},
            {'room_name': 'Unassigned', 'room_devices':[
                MockLexieDevice('1234').to_dict(),
                MockLexieDevice('4321').to_dict(),
            ]}
        ]
        return all_devices
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.lexiedevice.get_all_devices', mock_get_all_devices_with_rooms)
    res = client.get('/api/device/?groupby=rooms')
    assert json.loads(res.data) == [
        {'room_devices': [], 'room_name': 'Test room 1', 'room_id': '1234', 'room_visible': True},
        {'room_devices': [], 'room_name': 'Test room 2', 'room_id': '4321', 'room_visible': True},
        {'room_devices': [
            {
                'device_attributes': {'ip_address': '127.0.0.1'},
                'device_id': '1234',
                'device_manufacturer': 'shelly',
                'device_name': 'Mock device',
                'device_product': 'shelly1',
                'device_type': {'devicetype_id': 1, 'devicetype_name': 'Relay'},
                'room': {'room_id': '1234',
                'room_name': 'Test room 1'},
            },
            {
                'device_attributes': {'ip_address': '127.0.0.1'},
                'device_id': '4321',
                'device_manufacturer': 'shelly',
                'device_name': 'Mock device',
                'device_product': 'shelly1',
                'device_type': {'devicetype_id': 1, 'devicetype_name': 'Relay'},
                'room': {'room_id': '1234',
                'room_name': 'Test room 1'},
            }
        ],
        'room_name': 'Unassigned', 'room_id': None, 'room_visible': False}
    ]

def test_api_setup_events(monkeypatch, client):
    def mock_setup_events(self):
        global MOCK_CALLED
        MOCK_CALLED = "mock_setup_events"
        return True
    global MOCK_CALLED
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.setup_events', mock_setup_events)
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.supports_events', lambda self : True)
    res = client.get('/api/device/1234/setup-events')
    assert json.loads(res.data) == {
        "Result": "Success"
    }
    assert res.status_code == 200
    assert MOCK_CALLED == "mock_setup_events"

def test_api_setup_events_unsupported(monkeypatch, client):
    @property
    def mock_supports_events(self):
        global MOCK_CALLED
        MOCK_CALLED = "mock_supports_events"
        return False
    def mock_setup_events(self):
        global MOCK_CALLED
        MOCK_CALLED = "mock_setup_events_unsupported"
        return True
    global MOCK_CALLED
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.setup_events', mock_setup_events)
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.supports_events', mock_supports_events)
    res = client.get('/api/device/1234/setup-events')
    assert json.loads(res.data) == {
        "Error:": "Invalid command"
    }
    assert res.status_code == 200
    assert MOCK_CALLED != "mock_setup_events_unsupported"

def test_api_device_delete(monkeypatch, client):
    def mock_device_delete(self):
        global MOCK_CALLED
        MOCK_CALLED = True
        return

    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.delete', mock_device_delete)
    global MOCK_CALLED
    MOCK_CALLED = False
    result = client.delete('/api/device/1234')
    assert result.status_code ==200
    assert MOCK_CALLED is True

def test_api_device_delete_nonexisting(monkeypatch, client):
    def mock_device_delete(self, device_id):
        raise exceptions.NotFoundException

    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.__init__', mock_device_delete)
    # monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.delete', mock_device_delete)
    result = client.delete('/api/device/1234')
    assert result.status_code ==404

