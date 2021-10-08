import pytest
from lexie.smarthome.LexieDevice import LexieDeviceType
from lexie.smarthome.Room import Room

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

class MockRoom: #pylint: disable=too-few-public-methods
    """ mocks lexie.smarthome.Room.Room """
    def __init__(self, room_id = None):
        """ constructor """
        self.id = room_id
        self.name = 'Test room'

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
        self.room = Room('1234')

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
