import json
import logging
import socket

import requests
from flask import current_app

from lexie.smarthome.ILexieDevice import ILexieDevice


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
        self.device_id = device_data['device_id']
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

    @property
    def supports_events(self):
        """ This is quite static, because depends on the drivers. If the device supports calling a URL when turned on/off,
        this should return True, if not, return False """
        return True

    def setup_events(self):
        """ sets up Shelly device actions (output on/off) to call Lexie event urls
        returns True if success, False if not
        This should only ever be called, if supports_events returns True """
        lexie_url = current_app.config['LEXIE_URL']
        if self.__check_if_online():
            shelly_on_url = f"http://{self.device_ip}/settings/actions?index=0&name=out_on_url&enabled=true&urls[]={lexie_url}/events/{self.device_id}/on" # pylint: disable=line-too-long
            shelly_off_url = f"http://{self.device_ip}/settings/actions?index=0&name=out_off_url&enabled=true&urls[]={lexie_url}/events/{self.device_id}/off" # pylint: disable=line-too-long
            response_on = requests.get(shelly_on_url)
            response_off = requests.get(shelly_off_url)
            if response_on.status_code > 299 or response_off.status_code > 299:
                raise Exception(f'Shelly device {self.device_id} returned an error on HTTP call')
            return True
        raise Exception(f'Device {self.device_id} is offline.')
