from lexie.drivers.shelly import ShellyDevice


class HWDevice(ShellyDevice): # pylint: disable=too-few-public-methods
    """ Implements a Shelly 1 device """
    def __init__(self, device_data):
        """ constructor """
        super().__init__(device_data, 0)
