from typing import Any

from flask import current_app as app
from shortuuid import uuid  # type: ignore # pylint:disable=import-error

from lexie.db import get_db


class LexieDeviceType: #pylint: disable=too-few-public-methods
    """ represents LexieDevice types (Shelly1, Shelly DW, etc) from database """
    def __init__(self, devicetype_id: int) -> None:
        with app.app_context():
            lexie_db = get_db()
            devicetype = lexie_db.execute(
                "select devicetype_name, devicetype_manufacturer from devicetype where rowid=?",
                (devicetype_id,)
            ).fetchone()
            if devicetype is None:
                raise Exception("Invalid device type: %s" % devicetype_id) # pragma: nocover
            self.id = devicetype_id # pylint:disable=invalid-name
            self.name = devicetype['devicetype_name']
            self.manufacturer = devicetype['devicetype_manufacturer']

    def to_dict(self):
        """ returns a dict representaion of the object """
        temp_self = {
            'devicetype_id': self.id,
            'devicetype_name': self.name,
            'devicetype_manufacturer': self.manufacturer
        }
        return temp_self

class LexieDevice: # pylint: disable=too-few-public-methods
    """ A generic device class """
    def __init__(self, device_id: str):
        self.state: dict[str, Any] = {}
        with app.app_context():
            self.device_id = device_id
            lexie_db = get_db()
            device = lexie_db.execute(
                "select * from device where device_id=?", (device_id,)
            ).fetchone()
            if device is None:
                raise Exception('Device %s does not exist in database' % device_id)
        self.device_type = LexieDeviceType(device['device_type'])
        self.device_name = device['device_name']
        self.online = True
        self.ison = False

    @staticmethod
    def new(
        device_name: str,
        device_type: LexieDeviceType,
    ):
        """ Static method to store a new device in database.
        device_name and device_type are mandatory """
        device_id = uuid()
        with app.app_context():
            lexie_db = get_db()
            try:
                lexie_db.execute(
                    "INSERT INTO device (device_id, device_name, device_type) values (?, ?, ?)",
                    (device_id, device_name, device_type.id)
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
            'device_type': self.device_type.to_dict()
        }
        return temp_self
