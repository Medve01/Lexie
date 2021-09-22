import json
import logging
from typing import Any, Dict, Optional

from shortuuid import uuid  # type: ignore # pylint:disable=import-error

from .caching import get_value_from_cache, set_value_in_cache
from .ILexieDevice import ILexieDevice
from .models import Device, DeviceType, db
from .Room import Room


class LexieDeviceType: #pylint: disable=too-few-public-methods
    """ represents LexieDevice types (Shelly1, Shelly DW, etc) from database """
    def __init__(self, devicetype_id: int) -> None:
        devicetype = DeviceType.query.filter_by(id=devicetype_id).first()
        if devicetype_id is None:
            raise Exception(f'Invalid device type id: {devicetype_id}') # pragma: nocover
        self.id = devicetype.id # pylint:disable=invalid-name
        self.name = devicetype.name
        self.actions = []
        for action in json.loads(devicetype.actions):
            self.actions.append(action)
        # with app.app_context():
        #     lexie_db = get_db()
        #     devicetype = lexie_db.execute(
        #         "select devicetype_name, devicetype_actions from devicetype where rowid=?",
        #         (devicetype_id,)
        #     ).fetchone()
        #     if devicetype is None:
        #         raise Exception(f"Invalid device type: {devicetype_id}") # pragma: nocover
        #     self.id = devicetype_id # pylint:disable=invalid-name
        #     self.name = devicetype['devicetype_name']
        #     self.actions=[]
        #     for action in json.loads(devicetype['devicetype_actions']):
        #         self.actions.append(action)


    def to_dict(self):
        """ returns a dict representaion of the object """
        temp_self = {
            'devicetype_id': self.id,
            'devicetype_name': self.name,
        }
        return temp_self

class LexieDevice(ILexieDevice): # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """ A generic device class """
    def __init__(self, device_id: str):
        self.state: Dict[str, Any] = {}
        self.device_id = device_id
        device = Device.query.filter_by(id=device_id).first()
        if device is None:
            raise Exception(f'Device {device_id} does not exist in database')

        self.device_type = LexieDeviceType(device.device_type)
        self.device_name = device.name
        self.device_manufacturer = device.manufacturer
        self.device_product = device.product
        self.device_attributes = json.loads(device.attributes)
        driver = __import__('lexie.drivers.' + self.device_manufacturer + '.' + self.device_product,
                             globals(), locals(), ['HWDevice'], 0)
        self.hw_device = driver.HWDevice(self.to_dict())
        status = self.get_status()
        self.online = status["online"]
        self.ison = status["ison"]
        self.room: Optional[Room]=None
        if device.room_id is not None:
            self.room = Room(device.room_id)
        else:
            self.room = None

    @staticmethod
    def new(
        device_name: str,
        device_type: LexieDeviceType,
        device_product: str,
        device_manufacturer: str,
        device_attributes: Any
    ):
        """ Static method to store a new device in database.
        device_name and device_type are mandatory """
        device_id = uuid()
        device = Device(
            id=device_id,
            name = device_name,
            device_type = device_type.id,
            manufacturer = device_manufacturer,
            product = device_product,
            attributes = json.dumps(device_attributes)
        )
        db.session.add(device)
        db.session.commit()
        return LexieDevice(device_id=device_id)

    def to_dict(self):
        """ returns a dict representaion of the object """
        temp_self = {
            'device_id': self.device_id,
            'device_name': self.device_name,
            'device_type': self.device_type.to_dict(),
            'device_manufacturer': self.device_manufacturer,
            'device_product': self.device_product,
            'device_attributes': self.device_attributes,
        }
        if hasattr(self, 'ison'):
            temp_self['device_ison']= self.ison
        if hasattr(self, 'online'):
            temp_self['device_online'] = self.online
        return temp_self

# Driver methods
    def action_turn(self, ison:bool):
        """ turn relay on/off """
        result = self.hw_device.action_turn(ison)
        result['lexie_source'] = 'device'
        return result
    def action_toggle(self):
        """ toggle relay. implement param: relay no. """
        result = self.hw_device.action_toggle()
        result['lexie_source'] = 'device'
        return result
    def get_status(self, use_cache:bool = True): # pylint: disable=arguments-differ
        """  get relay status """
        device_status = None
        logging.debug('Fetching device status from cache (%s)', self.device_id)
        if use_cache:
            device_status = get_value_from_cache(self.device_id + "_status")
        if not device_status:
            logging.debug('Cache miss, fetching device status and storing in cache (%s)', self.device_id + "_status")
            device_status = self.hw_device.get_status()
            device_status_to_cache = device_status.copy()
            device_status_to_cache['lexie_source'] = "cache"
            set_value_in_cache(self.device_id + "_status", device_status_to_cache)
            device_status['lexie_source'] = 'device'
        self.online = device_status["online"]
        return device_status

    def move(self,room:Room) -> None:
        """ Moves a device from one room to another """
        device = db.session.query(Device).get(self.device_id)
        device.room_id = room.id
        db.session.commit()
        self.room = room


def get_all_devices():
    """ Fetches all devices from database and returns them in a list as LexieDevice objects """
    devices = []
    all_devices = Device.query.all()
    for device in all_devices:
        devices.append(LexieDevice(device_id = device.id))
    return devices
