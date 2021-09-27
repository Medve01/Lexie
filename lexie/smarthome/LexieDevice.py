import json
import logging
from typing import Any, Dict, Optional

from shortuuid import uuid  # type: ignore # pylint:disable=import-error

from lexie.caching import get_value_from_cache, set_value_in_cache
from lexie.smarthome import models
from lexie.smarthome.ILexieDevice import ILexieDevice
from lexie.smarthome.Room import Room


class LexieDeviceType: #pylint: disable=too-few-public-methods
    """ represents LexieDevice types (Shelly1, Shelly DW, etc) from database """
    def __init__(self, devicetype_id: int) -> None:
        devicetype = models.DeviceType.query.filter_by(id=devicetype_id).first()
        if devicetype_id is None:
            raise Exception(f'Invalid device type id: {devicetype_id}') # pragma: nocover
        self.id = devicetype.id # pylint:disable=invalid-name
        self.name = devicetype.name
        self.actions = []
        for action in json.loads(devicetype.actions):
            self.actions.append(action)

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
        device = models.Device.query.filter_by(id=device_id).first()
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
        device = models.Device(
            id=device_id,
            name = device_name,
            device_type = device_type.id,
            manufacturer = device_manufacturer,
            product = device_product,
            attributes = json.dumps(device_attributes)
        )
        models.db.session.add(device)
        models.db.session.commit()
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
        if hasattr(self, 'hw_device'):
            temp_self['supports_events'] = self.hw_device.supports_events
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
        device = models.db.session.query(models.Device).get(self.device_id)
        device.room_id = room.id
        models.db.session.commit()
        self.room = room

    @property
    def supports_events(self) -> bool:
        """ returns supports_events value from driver """
        return self.hw_device.supports_events

    def setup_events(self) -> bool:
        """ Calls HWDevice.setup_events() if it's supported """
        if self.hw_device.supports_events:
            return self.hw_device.setup_events()
        return False # pragma: nocover

    def set_status(self, status_name, status_value):
        """ checks if we have a status stored in cache and updates it with the parameters.
        If there's a cache miss, gets a full status to store it in cache"""
        device_status = get_value_from_cache(self.device_id + "_status")
        if not device_status:
            # cache miss, get full status
            self.get_status()
            return
        device_status[status_name] = status_value
        set_value_in_cache(self.device_id + "_status", device_status)


def get_all_devices():
    """ Fetches all devices from database and returns them in a list as LexieDevice objects """
    devices = []
    all_devices = models.Device.query.all()
    for device in all_devices:
        devices.append(LexieDevice(device_id = device.id))
    return devices
