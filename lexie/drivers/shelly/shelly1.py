import json
import logging
import socket
import urllib.request

import requests
from flask import current_app

from lexie.smarthome.ilexiedevice import ILexieDevice


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
            self.device_data['device_product'] != "shelly1":
            raise Exception(f'{device_data["device_id"]} is not a Shelly 1 device') # pragma: nocover
        self.device_ip = self.device_data['device_attributes']['ip_address']
        self.device_id = device_data["device_id"]
        self.supports_events = True
        logging.info("Shelly 1 device loaded. IP: %s", self.device_ip)

    def action_turn(self, ison:bool):
        """ turn relay on/off . implement param: relay no. """
        if ison:
            onoff = "on"
        else:
            onoff = "off"
        url = "http://" + self.device_ip + "/relay/0?turn=" + onoff
        logging.info('Checking if device is online')
        if self.__check_if_online():
            logging.info('Shelly1 driver: calling url %s', url)
            try:
                response = requests.get(url)
            except requests.exceptions.ConnectionError:
                return self.response_to_status(None)
            return self.response_to_status(response)
        return self.response_to_status(None) # TODO: create a test for this case #pylint: disable=fixme #pragma: nocover

    def action_toggle(self):
        """ toggle relay. implement param: relay no. """
        url = "http://" + self.device_ip + "/relay/0?turn=toggle"
        logging.info('Shelly1 driver: calling url %s', url)
        if self.__check_if_online():
            try:
                response = requests.get(url)
            except requests.exceptions.ConnectionError:
                return self.response_to_status(None)
            return self.response_to_status(response)
        return self.response_to_status(None) # TODO: create a test for this case #pylint: disable=fixme #pragma: nocover

    def get_status(self):
        """  get relay status """
        if self.__check_if_online():
            url = "http://" + self.device_ip + "/relay/0"
            logging.info('Shelly1 driver: calling url %s', url)
            try:
                response = requests.get(url)
            except requests.exceptions.ConnectionError:
                return self.response_to_status(None)
            return self.response_to_status(response)
        return self.response_to_status(None)

    def setup_events(self):
        """ sets up Shelly device actions (output on/off) to call Lexie event urls
        returns True if success, False if not
        This should only ever be called, if supports_events returns True """
        lexie_url = current_app.config['LEXIE_URL']
        if self.__check_if_online():
            shelly_url = f"http://{self.device_ip}/settings/actions"
            on_params = "index=0&name=out_on_url&enabled=true&urls[]=" + lexie_url + "/events/" + self.device_id + "/on"
            off_params = "index=0&name=out_off_url&enabled=true&urls[]=" + lexie_url + "/events/" + self.device_id + "/off"
            # request.get always urlencodes the parameters and Shelly doesn't repond well to that. Therefore using urlopen here.
            response_on = urllib.request.urlopen(shelly_url + "?" + on_params) # pylint: disable=consider-using-with # nosec # shelly_url is always http, it's hardcoded
            response_off = urllib.request.urlopen(shelly_url + "?" + off_params) # pylint: disable=consider-using-with # nosec # shelly_url is always http, it's hardcoded
            if response_on.status > 299 or response_off.status > 299:
                raise Exception(f'Shelly device {self.device_id} returned an error on HTTP call')
            # reading back settings for verification
            result = requests.get(shelly_url)
            result_obj = json.loads(result.text)
            if (
                result_obj["actions"]["out_on_url"][0]["urls"][0] != lexie_url + "/events/" + self.device_id + "/on" or
                result_obj["actions"]["out_on_url"][0]["index"] != 0 or
                result_obj["actions"]["out_on_url"][0]["enabled"] is not True
            ):
                raise Exception("Unexpected results when verifying Shelly action url setup. There's a bug in the driver, or you need to update it.")
            return True
        raise Exception(f'Device {self.device_id} is offline.')
