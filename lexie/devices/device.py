from typing import Any

from flask import current_app as app
from shortuuid import uuid  # type: ignore # pylint:disable=import-error

from lexie.db import get_db


class LexieDevice: # pylint: disable=too-few-public-methods
    """ A generic device class """
    def __init__(self, device_id: str):
        self.state: dict[str, Any] = {}
        with app.app_context():
            self.device_id = device_id
            lexie_db = get_db()
            device = lexie_db.execute(
                "SELECT * FROM device WHERE device_id = ?", (device_id,)
            ).fetchone()
        if device is None:
            raise Exception('Device does %s not exist in database' % device_id)
        self.device_type = device['device_type']
        self.device_name = device['device_name']
        self.online = True
        self.ison = False


    def status(self):
        """returns a device status as a dict"""
        status_dict: dict(str, Any) = {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "device_type": self.device_type,
            "online": self.online,
            "ison": self.ison,
        }
        return status_dict

    @staticmethod
    def new(
        device_name: str,
        device_type: str,
    ):
        """ Static method to store a new device in database.
        device_name and device_type are mandatory """
        device_id = uuid()
        with app.app_context():
            lexie_db = get_db()
            try:
                lexie_db.execute(
                    "INSERT INTO device (device_id, device_name, device_type) values (?, ?, ?)",
                    (device_id, device_name, device_type)
                )
                lexie_db.commit()
            except Exception: # pragma: nocover
                print('Database error')
                raise
            return LexieDevice(device_id = device_id)
