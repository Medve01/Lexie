from typing import Any


class LexieDevice: # pylint: disable=too-few-public-methods
    """ A generic device class """
    def __init__(self, device_id: str):
        self.state: dict[str, Any] = {}
        self.online = True
        self.ison = False
        self.device_id = device_id


    def status(self):
        """returns a device status as a dict"""
        status_dict: dict(str, Any) = {
            "online": self.online,
            "ison": self.ison,
            "device_id": self.device_id
        }
        return status_dict
