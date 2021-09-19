import json
import logging
from typing import Any, Dict

from flask import current_app as app
from shortuuid import uuid  # type: ignore # pylint:disable=import-error

from lexie.caching import get_value_from_cache, set_value_in_cache
from lexie.db import get_db
from lexie.devices.ILexieDevice import ILexieDevice


class LexieDeviceType: #pylint: disable=too-few-public-methods
    """ represents LexieDevice types (Shelly1, Shelly DW, etc) from database """
    def __init__(self, devicetype_id: int) -> None:
        with app.app_context():
            lexie_db = get_db()
            devicetype = lexie_db.execute(
                "select devicetype_name, devicetype_actions from devicetype where rowid=?",
                (devicetype_id,)
            ).fetchone()
            if devicetype is None:
                raise Exception(f"Invalid device type: {devicetype_id}") # pragma: nocover
            self.id = devicetype_id # pylint:disable=invalid-name
            self.name = devicetype['devicetype_name']
            self.actions=[]
            for action in json.loads(devicetype['devicetype_actions']):
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
        with app.app_context():
            self.device_id = device_id
            lexie_db = get_db()
            device = lexie_db.execute(
                "select * from device, device_attributes where device.device_id = device_attributes.device_id and  device.device_id=?", (device_id,) #pylint: disable=line-too-long
            ).fetchone()
            if device is None:
                raise Exception(f'Device {device_id} does not exist in database')
        self.device_type = LexieDeviceType(device['device_type'])
        self.device_name = device['device_name']
        self.device_manufacturer = device['device_manufacturer']
        self.device_product = device['device_product']
        self.device_attributes = json.loads(device['device_attributes'])
        driver = __import__('lexie.drivers.' + self.device_manufacturer + '.' + self.device_product,
                             globals(), locals(), ['HWDevice'], 0)
        self.hw_device = driver.HWDevice(self.to_dict())
        status = self.get_status()
        self.online = status["online"]
        self.ison = status["ison"]

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
        with app.app_context():
            lexie_db = get_db()
            try:
                lexie_db.execute(
                    "INSERT INTO device (device_id, device_name, device_type, device_manufacturer, device_product) values (?, ?, ?, ?, ?)",
                    (device_id, device_name, device_type.id, device_manufacturer, device_product)
                )
                lexie_db.commit()
                lexie_db.execute(
                    'INSERT INTO device_attributes (device_id, device_attributes) values (?, ?)',
                    (device_id, json.dumps(device_attributes))
                )
                lexie_db.commit()
            except Exception: # pragma: nocover
                print('Database error')
                raise
            return LexieDevice(device_id = device_id)

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

def get_all_devices():
    """ Fetches all devices from database and returns them in a list as LexieDevice objects """
    with app.app_context():
        lexie_db = get_db()
        device_ids = lexie_db.execute(
            "select device_id from device"
        ).fetchall()
        devices = []
        for device_id in device_ids:
            devices.append(LexieDevice(device_id['device_id']))
        return devices
