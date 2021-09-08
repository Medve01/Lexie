import json
import logging

import requests

from lexie.devices.ILexieDevice import ILexieDevice


class HWDevice(ILexieDevice): # pylint: disable=too-few-public-methods
    """ Implements a Shelly 1 device """
    @staticmethod
    def response_to_status(response):
        """ creates the generalized response LexieDevice accepts from Shelly1 status
        attributes expected
        "has_timer": False,
        "ison": False,
        "source": "http",
        "timer_duration": 0,
        "timer_remaining": 0,
        "timer_started": 0,
        "lexie_source": "cache" """
        if not response:
            return {
                'ison': None,
                'online': False
            }
        status = json.loads(response.text)
        return {
            'ison': status['ison'],
            'online': True
        }



    def __init__(self, device_data):
        """ constructor """
        self.device_data = device_data
        if self.device_data['device_manufacturer'] != "shelly" and \
            self.device_data['device_type'] != 1 and \
            self.device_data['device_product'] != "shelly1":
            raise Exception('%s is not a Shelly 1 device' % device_data['device_id']) # pragma: nocover
        self.device_ip = self.device_data['device_attributes']['ip_address']
        logging.info("Shelly 1 device loaded. IP: %s", self.device_ip)

    def relay_action_set(self, ison:bool):
        """ turn relay on/off . implement param: relay no. """
        if ison:
            onoff = "on"
        else:
            onoff = "off"
        url = "http://" + self.device_ip + "/relay/0?turn=" + onoff
        logging.info('Shelly1 driver: calling url %s', url)
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            return self.response_to_status(None)
        return self.response_to_status(response)

    def relay_action_toggle(self):
        """ toggle relay. implement param: relay no. """
        url = "http://" + self.device_ip + "/relay/0?turn=toggle"
        logging.info('Shelly1 driver: calling url %s', url)
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            return self.response_to_status(None)
        return self.response_to_status(response)

    def relay_property_get_status(self):
        """  get relay status """
        url = "http://" + self.device_ip + "/relay/0"
        logging.info('Shelly1 driver: calling url %s', url)
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            return self.response_to_status(None)
        return self.response_to_status(response)
