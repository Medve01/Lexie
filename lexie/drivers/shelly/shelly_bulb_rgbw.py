import json
import logging
import socket

import requests

from ...smarthome.ILexieDevice import ILexieDevice


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

    def __check_if_online(self):
        """ checks if a device is online by connecting to port 80 """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)                                      #1 Second Timeout
        result = sock.connect_ex((self.device_ip,80))
        return result == 0


    def __init__(self, device_data):
        """ constructor """
        self.device_data = device_data
        if self.device_data['device_manufacturer'] != "shelly" and \
            self.device_data['device_type'] != 1 and \
            self.device_data['device_product'] != "shelly_bulb_rgbw":
            raise Exception(f'{device_data["device_id"]} is not a Shelly 1 device') # pragma: nocover
        self.device_ip = self.device_data['device_attributes']['ip_address']
        logging.info("Shelly 1 device loaded. IP: %s", self.device_ip)

    def action_turn(self, ison:bool):
        """ turn light on/off """
        if ison:
            onoff = "on"
        else:
            onoff = "off"
        url = "http://" + self.device_ip + "/light/0?turn=" + onoff
        logging.info('Shelly Bulb RGBW driver: calling url %s', url)
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            return self.response_to_status(None)
        return self.response_to_status(response)

    def action_toggle(self):
        """ toggle light """
        url = "http://" + self.device_ip + "/light/0?turn=toggle"
        logging.info('Shelly Bulb RGBW driver: calling url %s', url)
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            return self.response_to_status(None)
        return self.response_to_status(response)

    def get_status(self):
        """  get relay status """
        if self.__check_if_online():
            url = "http://" + self.device_ip + "/light/0"
            logging.info('Shelly Bulb RGBW driver: calling url %s', url)
            try:
                response = requests.get(url)
            except requests.exceptions.ConnectionError:
                return self.response_to_status(None)
            return self.response_to_status(response)
        return self.response_to_status(None)
