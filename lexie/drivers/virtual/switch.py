import logging
from flask import current_app

from lexie.smarthome.ILexieDevice import ILexieDevice


class HWDevice(ILexieDevice): # pylint: disable=too-few-public-methods
    """ Implements a Virtual Switch device """
    def __init__(self, device_data):
        """ constructor """
        self.device_data = device_data
        if self.device_data['device_manufacturer'] != "virtual" and \
            self.device_data['device_type'] != 1 and \
            self.device_data['device_product'] != "switch":
            raise Exception(f'{device_data["device_id"]} is not a Virtual Switch device') # pragma: nocover
        self.device_id = device_data["device_id"]
        self.supports_events = True
        self.ison = True
        logging.info("Virtual switch device loaded. ")

    def action_turn(self, ison:bool):
        """ turn relay on/off . implement param: relay no. """
        if ison:
            self.ison = True
        else:
            self.ison = False
        return {'online': True, 'ison': self.ison}
        ## Todo: send in events

    def action_toggle(self):
        if self.ison:
            return self.action_turn(False)
        return self.action_turn(True)

    def get_status(self):
        """  get relay status """
        return {'online': True, 'ison': self.ison}

    def setup_events(self): # pylint: disable=no-self-use
        """ sets up Shelly device actions (output on/off) to call Lexie event urls
        returns True if success, False if not
        This should only ever be called, if supports_events returns True """
        return True
