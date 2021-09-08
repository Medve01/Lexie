import json
import logging

import requests

from lexie.devices.ILexieDevice import ILexieDevice


class HWDevice(ILexieDevice): # pylint: disable=too-few-public-methods
    """ Implements a Shelly 1 device """
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
        response = requests.get(url)
        if response:
            return json.loads(response.text)
        raise Exception('Shelly 1 API call failed!') # pragma: nocover

    def relay_action_toggle(self):
        """ toggle relay. implement param: relay no. """
        url = "http://" + self.device_ip + "/relay/0?turn=toggle"
        logging.info('Shelly1 driver: calling url %s', url)
        response = requests.get(url)
        if response:
            return json.loads(response.text)
        raise Exception('Shelly 1 API call failed!') # pragma: nocover
    def relay_property_get_status(self):
        """  get relay status """
        url = "http://" + self.device_ip + "/relay/0"
        logging.info('Shelly1 driver: calling url %s', url)
        response = requests.get(url)
        if response:
            return json.loads(response.text)
        raise Exception('Shelly 1 API call failed!') # pragma: nocover

# will need to implement actions here. Turn on/off, setup, etc.
# How to handle on/off statuses? store it in memory? Maybe memcached, so it can be read/written?
# For now I'll go with directly querying the device itself, on every ison get,
# but this will not be futureproof at all, ever.
