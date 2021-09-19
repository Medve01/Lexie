import requests
import pytest

from lexie.drivers.shelly.shelly_bulb_rgbw import HWDevice


device_data={
                "device_id": "123456",
                "device_name": "Mock device",
                "device_attributes": {"ip_address": "127.0.0.1"},
                "device_manufacturer": "shelly",
                "device_product": "shelly_bulb_rgbw",
                "device_type": 2
            }

def test_shelly_bulb_rgbw_init():
    """ tests if ip address is loaded successfully """
    testdevice = HWDevice(device_data)
    assert testdevice.device_ip == "127.0.0.1"

@pytest.mark.parametrize("onoff, results",
    [
        (
            True,
            {
                "ison": True,
                "online": True
            },
        ),
        (
            False,
            {
                "ison": False,
                "online": True
            }
        ),
    ]
)
def test_shelly_bulb_rgbw_turn_onoff(monkeypatch, onoff, results):
    """ tests if we can turn a shelly 1 on """
    class MockResponse(object):
        def __init__(self, url) -> None:
            self.status_code = 200
            self.url = url
            if url.split("=")[1] == "on":
                self.text = '{"ison":true,"source":"http","has_timer":false,"timer_started":0,"timer_duration":0,"timer_remaining":0,"mode":"color","red":255,"green":0,"blue":0,"gain":100,"effect":1,"transition":0}' # pylint: disable=line-too-long
            elif url.split("=")[1] == "off":
                self.text = '{"ison":false,"source":"http","has_timer":false,"timer_started":0,"timer_duration":0,"timer_remaining":0,"mode":"color","red":255,"green":0,"blue":0,"gain":100,"effect":1,"transition":0}' # pylint: disable=line-too-long
            else:
                self.text = '{"Error": "Invalid command"}'
    def mock_get(url):
        return MockResponse(url)
    monkeypatch.setattr(requests, 'get', mock_get)
    testdevice = HWDevice(device_data)

    assert testdevice.action_turn(onoff) == results

def test_shelly_bulb_rgbw_turn_onoff_unavailable(monkeypatch):
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
        raise requests.exceptions.ConnectionError
    monkeypatch.setattr(requests, 'get', mock_get)
    testdevice = HWDevice(device_data)

    assert testdevice.action_turn(True) == {
                "ison": None,
                "online": False
            }

def test_shelly_bulb_rgbw_toggle(monkeypatch):
    """ tests toggle """
    class MockResponse(object):
        def __init__(self, url) -> None:
            self.status_code = 200
            self.url = url
            self.text = '{"ison":false,"source":"http","has_timer":false,"timer_started":0,"timer_duration":0,"timer_remaining":0,"mode":"color","red":255,"green":0,"blue":0,"gain":100,"effect":1,"transition":0}' # pylint: disable=line-too-long
    def mock_get(url):
        return MockResponse(url)
    monkeypatch.setattr(requests, 'get', mock_get)
    testdevice = HWDevice(device_data)
    assert testdevice.action_toggle() == {
                                                    "ison": False,
                                                    "online": True
                                                }

def test_shelly_bulb_rgbw_toggle_unavailable(monkeypatch):
    """ tests toggle """
    class MockResponse(object):
        def __init__(self, url) -> None:
            pass
    def mock_get(url):
        raise requests.exceptions.ConnectionError
    monkeypatch.setattr(requests, 'get', mock_get)
    testdevice = HWDevice(device_data)
    assert testdevice.action_toggle() == {
                                                    "ison": None,
                                                    "online": False
                                                }

def test_shelly_bulb_rgbw_get_status(monkeypatch):
    """ tests get status call """
    class MockSocket(object):
        def __init__(self, family=-1, type=-1, proto=-1, fileno=None) -> None:
            pass

    def mock_socket_settimeout(self, timeout):
        return
    def mock_sock_connect_ex(self, target):
        return 0
    
    class MockResponse(object):
        def __init__(self, url) -> None:
            self.status_code = 200
            self.url = url
            self.text = '{"ison":false,"source":"http","has_timer":false,"timer_started":0,"timer_duration":0,"timer_remaining":0,"mode":"color","red":255,"green":0,"blue":0,"gain":100,"effect":1,"transition":0}' # pylint: disable=line-too-long
    def mock_get(url):
        return MockResponse(url)

    def mock_sock_connect_ex(self, target):
        return 0
    monkeypatch.setattr(requests, 'get', mock_get)
    import socket
    monkeypatch.setattr('socket.socket.__init__', MockSocket.__init__)
    monkeypatch.setattr('socket.socket.settimeout', mock_socket_settimeout)
    monkeypatch.setattr('socket.socket.connect_ex', mock_sock_connect_ex)
    testdevice = HWDevice(device_data)

    assert testdevice.get_status() == {
                                                    "ison": False,
                                                    "online": True
                                                }

def test_shelly_bulb_rgbw_get_status_no_response(monkeypatch):
    """ tests get status call """
    class MockSocket(object):
        def __init__(self, family=-1, type=-1, proto=-1, fileno=None) -> None:
            pass

    def mock_socket_settimeout(self, timeout):
        return
    def mock_sock_connect_ex(self, target):
        return 0

    class MockResponse(object):
        def __init__(self, url) -> None:
            self.status_code = 200
            self.url = url
            self.text = '{"ison":false,"source":"http","has_timer":false,"timer_started":0,"timer_duration":0,"timer_remaining":0,"mode":"color","red":255,"green":0,"blue":0,"gain":100,"effect":1,"transition":0}' # pylint: disable=line-too-long
    def mock_get(url):
        raise requests.exceptions.ConnectionError
    monkeypatch.setattr('socket.socket.__init__', MockSocket.__init__)
    monkeypatch.setattr('socket.socket.settimeout', mock_socket_settimeout)
    monkeypatch.setattr('socket.socket.connect_ex', mock_sock_connect_ex)
    monkeypatch.setattr(requests, 'get', mock_get)
    testdevice = HWDevice(device_data)
    assert testdevice.get_status() == {
                                                    "ison": None,
                                                    "online": False
                                                }


def test_shelly_bulb_rgbw_get_status_socket_error(monkeypatch):
    """ tests get status call """
    class MockSocket(object):
        def __init__(self, family=-1, type=-1, proto=-1, fileno=None) -> None:
            pass

    def mock_socket_settimeout(self, timeout):
        return
    def mock_sock_connect_ex(self, target):
        return 1
    monkeypatch.setattr('socket.socket.__init__', MockSocket.__init__)
    monkeypatch.setattr('socket.socket.settimeout', mock_socket_settimeout)
    monkeypatch.setattr('socket.socket.connect_ex', mock_sock_connect_ex)

    testdevice = HWDevice(device_data)
    assert testdevice.get_status() == {
                                                    "ison": None,
                                                    "online": False
                                                }