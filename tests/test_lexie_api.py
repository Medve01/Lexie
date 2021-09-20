import json
from typing import Any
import pytest
from lexie.lexie_app import create_app
from lexie.db import init__db
from lexie.smarthome.LexieDevice import LexieDeviceType


device_data={
                "device_id": "123456",
                "device_name": "Mock device",
                "device_attributes": {"ip_address": "127.0.0.1"},
                "device_manufacturer": "shelly",
                "device_product": "shelly1",
                "device_type": 1,
                "device_online": "ONLINE",
                "device_ison": "ON"
            }


class MockLexieDevice: #pylint: disable=too-few-public-methods
    """ mocks LexieDevice so we can test the http endpoint only """
    def __init__(self, device_id): #pylint: disable=redefined-outer-name
        """ constructor """
        self.device_id = device_id
        self.device_name = device_data['device_name']
        self.device_type = LexieDeviceType(device_data['device_type'])
        self.device_product = device_data['device_product']
        self.device_manufacturer = device_data['device_manufacturer']
        self.device_attributes = device_data['device_attributes']
        self.device_ison = device_data['device_ison']
        self.device_online = device_data['device_online']

    def action_turn(self, onoff): #pylint: disable=no-self-use
        """ returns a mocked response of HWDevice.action_turn """
        if onoff:
            return  {
                        "ison": True,
                        "online": True,
                        "lexie_source": "device"
                    }
        return  {
                    "ison": False,
                    "online": True,
                    "lexie_source": "device"
                }
    def action_toggle(self): #pylint: disable=no-self-use
        """ returns a mocked response of HWDevice.action_turn """
        return  {
                    "ison": False,
                    "online": True,
                    "lexie_source": "device"
                }

    def to_dict(self):
        temp_self = {
            'device_id': self.device_id,
            'device_name': self.device_name,
            'device_type': self.device_type.to_dict(),
            'device_manufacturer': self.device_manufacturer,
            'device_product': self.device_product,
            'device_attributes': self.device_attributes,
            'device_ison': self.device_ison,
            'device_online': self.device_online
        }
        return temp_self


@pytest.fixture
def app():
    _app = create_app(testing=True)
    with _app.app_context():
        init__db()
    return _app


@pytest.fixture
def client(app):
    _client = app.test_client()
    return _client


def test_api_get_device(monkeypatch, client):
    """" tests /api/device/device_id"""
    def mocklexiedevice_init(Any, device_id):
        return MockLexieDevice(device_id)
    
    def mocklexiedevice_to_dict(Any):
        mock_device = MockLexieDevice('1234')
        return mock_device.to_dict()
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.to_dict', mocklexiedevice_to_dict)
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


    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.action_turn', mock_action_turn)
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.action_toggle', mock_action_toggle)
    res = client.get('/api/device/1234/' + onoff)
    assert json.loads(res.data) == results

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
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.new', new_lexiedevice)
    # monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', mock_lexiedevice_init)
    res = client.put('/api/device', data=json.dumps(device_data))
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
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.LexieDevice.get_all_devices', mock_get_all_devices)
    res = client.get('/api/device')
    assert json.loads(res.data) == [
        {'device_attributes': {'ip_address': '127.0.0.1'},
        'device_id': '1234',
        'device_manufacturer': 'shelly',
        'device_name': 'Mock device',
        'device_product': 'shelly1',
        'device_type': {'devicetype_id': 1,
            'devicetype_name': 'Relay'}},
        {'device_attributes': {'ip_address': '127.0.0.1'},
        'device_id': '4321',
        'device_manufacturer': 'shelly',
        'device_name': 'Mock device',
        'device_product': 'shelly1',
        'device_type': {'devicetype_id': 1,
        'devicetype_name': 'Relay'}},
    ]
