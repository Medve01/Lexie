import logging

import requests
from flask import current_app

from lexie import caching
from lexie.smarthome.events import send_event
from lexie.smarthome.ilexiedevice import ILexieDevice


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
        cached_data = caching.get_value_from_cache(f'virtual_switch_{self.device_id}')
        if cached_data is None:
            caching.set_value_in_cache(f'virtual_switch_{self.device_id}', {'ison': False})
            cached_data = {'ison': False}
        self.supports_events = True
        self.ison = cached_data['ison']
        logging.info("Virtual switch device loaded. ")

    def action_turn(self, ison:bool):
        """ turn relay on/off . implement param: relay no. """
        if ison:
            self.ison = True
        else:
            self.ison = False
        caching.set_value_in_cache(f'virtual_switch_{self.device_id}', {'ison': self.ison})
        if self.ison:
            event = 'on'
        else:
            event = 'off'
        send_event(device_id=self.device_id, event=event, event_type='status')
        return {'online': True, 'ison': self.ison}

    def action_toggle(self):
        if self.ison:
            return self.action_turn(False)
        return self.action_turn(True)

    def get_status(self):
        """  get relay status """
        cached_data = caching.get_value_from_cache(f'virtual_switch_{self.device_id}')
        return {'online': True, 'ison': cached_data['ison']}

    def setup_events(self): # pylint: disable=no-self-use
        """ sets up Shelly device actions (output on/off) to call Lexie event urls
        returns True if success, False if not
        This should only ever be called, if supports_events returns True """
        return True
