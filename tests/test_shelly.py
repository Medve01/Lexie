import requests
import pytest
from unittest import mock

from lexie.drivers.shelly.shelly1 import HWDevice


device_data={
                "device_id": "123456",
                "device_name": "Mock device",
                "device_attributes": {"ip_address": "127.0.0.1"},
                "device_manufacturer": "shelly",
                "device_product": "shelly1",
                "device_type": 1
            }

def test_shelly1_init():
    """ tests if ip address is loaded successfully """
    testdevice = HWDevice(device_data)
    assert testdevice.device_ip == "127.0.0.1"

# @mock.patch('lexie.drivers.shelly.shelly1.requests.get')
@pytest.mark.parametrize("onoff, results",
    [
        (
            True,
            {
                "has_timer": False,
                "ison": True,
                "source": "http",
                "timer_duration": 0,
                "timer_remaining": 0,
                "timer_started": 0
            }
        ),
        (
            False,
            {
                "has_timer": False,
                "ison": False,
                "source": "http",
                "timer_duration": 0,
                "timer_remaining": 0,
                "timer_started": 0
            }
        )
    ]
)
def test_shelly1_turn_onoff(monkeypatch, onoff, results):
    """ tests if we can turn a shelly 1 on """
    class MockResponse(object):
        def __init__(self, url) -> None:
            self.status_code = 200
            self.url = url
            if url.split("=")[1] == "on":
                self.text = '{"has_timer": false,"ison": true,"source": "http","timer_duration": 0,"timer_remaining": 0,"timer_started": 0}' # pylint: disable=line-too-long
            elif url.split("=")[1] == "off":
                self.text = '{"has_timer": false,"ison": false,"source": "http","timer_duration": 0,"timer_remaining": 0,"timer_started": 0}' # pylint: disable=line-too-long
            else:
                self.text = '{"Error": "Invalid command"}'
    def mock_get(url):
        return MockResponse(url)
    monkeypatch.setattr(requests, 'get', mock_get)
    testdevice = HWDevice(device_data)

    assert testdevice.relay_action_set(onoff) == results

def test_shelly1_toggle(monkeypatch):
    """ tests toggle """
    class MockResponse(object):
        def __init__(self, url) -> None:
            self.status_code = 200
            self.url = url
            self.text = '{"has_timer": false,"ison": false,"source": "http","timer_duration": 0,"timer_remaining": 0,"timer_started": 0}' # pylint: disable=line-too-long
    def mock_get(url):
        return MockResponse(url)
    monkeypatch.setattr(requests, 'get', mock_get)
    testdevice = HWDevice(device_data)
    assert testdevice.relay_action_toggle() == {
                                                    "has_timer": False,
                                                    "ison": False,
                                                    "source": "http",
                                                    "timer_duration": 0,
                                                    "timer_remaining": 0,
                                                    "timer_started": 0
                                                }

def test_shelly1_get_status(monkeypatch):
    """ tests get status call """
    class MockResponse(object):
        def __init__(self, url) -> None:
            self.status_code = 200
            self.url = url
            self.text = '{"has_timer": false,"ison": false,"source": "http","timer_duration": 0,"timer_remaining": 0,"timer_started": 0}'
    def mock_get(url):
        return MockResponse(url)
    monkeypatch.setattr(requests, 'get', mock_get)
    testdevice = HWDevice(device_data)
    assert testdevice.relay_property_get_status == {
                                                    "has_timer": False,
                                                    "ison": False,
                                                    "source": "http",
                                                    "timer_duration": 0,
                                                    "timer_remaining": 0,
                                                    "timer_started": 0
                                                }
