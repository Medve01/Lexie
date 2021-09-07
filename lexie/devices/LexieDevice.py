import json
from typing import Any

from flask import current_app as app
from shortuuid import uuid  # type: ignore # pylint:disable=import-error

from lexie.db import get_db
from lexie.devices.ILexieDevice import ILexieDevice


class LexieDeviceType: #pylint: disable=too-few-public-methods
    """ represents LexieDevice types (Shelly1, Shelly DW, etc) from database """
    def __init__(self, devicetype_id: int) -> None:
        with app.app_context():
            lexie_db = get_db()
            devicetype = lexie_db.execute(
                "select devicetype_name from devicetype where rowid=?",
                (devicetype_id,)
            ).fetchone()
            if devicetype is None:
                raise Exception("Invalid device type: %s" % devicetype_id) # pragma: nocover
            self.id = devicetype_id # pylint:disable=invalid-name
            self.name = devicetype['devicetype_name']


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
        self.state: dict[str, Any] = {}
        with app.app_context():
            self.device_id = device_id
            lexie_db = get_db()
            device = lexie_db.execute(
                "select * from device, device_attributes where device.device_id = device_attributes.device_id and  device.device_id=?", (device_id,) #pylint: disable=line-too-long
            ).fetchone()
            if device is None:
                raise Exception('Device %s does not exist in database' % device_id)
        self.device_type = LexieDeviceType(device['device_type'])
        self.device_name = device['device_name']
        self.online = True
        self.ison = False
        self.device_manufacturer = device['device_manufacturer']
        self.device_product = device['device_product']
        self.device_attributes = json.loads(device['device_attributes'])
        driver = __import__('lexie.drivers.' + self.device_manufacturer + '.' + self.device_product,
                             globals(), locals(), ['HWDevice'], 0)
        self.hw_device = driver.HWDevice(self.to_dict())
            # if device_type is Shelly1
            # driver = __import__('lexie.drivers.shelly.shelly1', globals(), locals(), ['Shelly1Device'], 0) # pylint: disable=line-too-long
            # OR... import module name is concatenated intto he function! so it's completely dynamic. Need to have a module_name in the devicetype table. and fuck you pylint and your too long omment lines # pylint: disable=line-too-long

    # def get_raw_data(self):
    #     """ gets raw device data from database for use in device drivers """
    #     with app.app_context():
    #         lexie_db = get_db()
    #         try:
    #             results = lexie_db.execute(
    #                 "select * from device where device_id = ?", (self.device_id,)
    #             ).fetchone()
    #         except Exception: # pragma: nocover
    #             print("Database error")
    #             raise
    #         if results is None:
    #             raise Exception('No such device in database %s' % self.device_id)
    #         return results

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
                lexie_db.execute('INSERT INTO device_attributes (device_id, device_attributes) values (?, ?)', (device_id, json.dumps(device_attributes)))
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
            'device_attributes': self.device_attributes
        }
        return temp_self

# Driver methods
    def relay_action_set(self, ison:bool):
        """ turn relay on/off """
        return self.hw_device.relay_action_set(ison)
    def relay_action_toggle(self):
        """ toggle relay. implement param: relay no. """
        return self.hw_device.relay_action_toggle()
    @property
    def relay_property_get_status(self):
        """  get relay status """
        return self.hw_device.relay_property_get_status()
