import json
import pytest
import requests

from lexie.drivers.shelly.shelly1 import HWDevice
from tests.fixtures.test_flask_app import app

device_data={
                "device_id": "123456",
                "device_name": "Mock device",
                "device_attributes": {"ip_address": "127.0.0.1"},
                "device_manufacturer": "shelly",
                "device_product": "shelly1",
                "device_type": 1
            }

MOCK_PARAMS: str = []


def test_shelly1_init():
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
    def mock_socket_connect_ex(ip, port):
        return 0
    monkeypatch.setattr('socket.socket.connect_ex', mock_socket_connect_ex)
    monkeypatch.setattr(requests, 'get', mock_get)
    testdevice = HWDevice(device_data)

    assert testdevice.action_turn(onoff) == results

def test_shelly1_turn_onoff_unavailable(monkeypatch):
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
    def mock_socket_connect_ex(ip, port):
        return 0
    monkeypatch.setattr('socket.socket.connect_ex', mock_socket_connect_ex)
    monkeypatch.setattr(requests, 'get', mock_get)
    testdevice = HWDevice(device_data)

    assert testdevice.action_turn(True) == {
                "ison": None,
                "online": False
            }

def test_shelly1_toggle(monkeypatch):
    """ tests toggle """
    class MockResponse(object):
        def __init__(self, url) -> None:
            self.status_code = 200
            self.url = url
            self.text = '{"has_timer": false,"ison": false,"source": "http","timer_duration": 0,"timer_remaining": 0,"timer_started": 0}' # pylint: disable=line-too-long
    def mock_get(url):
        return MockResponse(url)
    def mock_socket_connect_ex(ip, port):
        return 0
    monkeypatch.setattr('socket.socket.connect_ex', mock_socket_connect_ex)
    monkeypatch.setattr(requests, 'get', mock_get)
    testdevice = HWDevice(device_data)
    response = testdevice.action_toggle()
    assert response == {
                                                    "ison": False,
                                                    "online": True
                                                }

def test_shelly1_toggle_unavailable(monkeypatch):
    """ tests toggle """
    class MockResponse(object):
        def __init__(self, url) -> None:
            pass
    def mock_get(url):
        raise requests.exceptions.ConnectionError
    def mock_socket_connect_ex(ip, port):
        return 0
    monkeypatch.setattr('socket.socket.connect_ex', mock_socket_connect_ex)
    monkeypatch.setattr(requests, 'get', mock_get)
    testdevice = HWDevice(device_data)
    assert testdevice.action_toggle() == {
                                                    "ison": None,
                                                    "online": False
                                                }

def test_shelly1_get_status(monkeypatch):
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
            self.text = '{"has_timer": false,"ison": false,"source": "http","timer_duration": 0,"timer_remaining": 0,"timer_started": 0}'
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

def test_shelly1_get_status_no_response(monkeypatch):
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
            self.text = '{"has_timer": false,"ison": false,"source": "http","timer_duration": 0,"timer_remaining": 0,"timer_started": 0}'
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


def test_shelly1_get_status_socket_error(monkeypatch):
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

def test_shelly1_supports_events():
    """ tests if the driver returns true, it should """

    testdevice = HWDevice(device_data)
    assert testdevice.supports_events == True

def test_shelly1_setup_events_success(monkeypatch, app):
    """ Tests event setup """
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
            self.text = json.dumps(
                {
                    "actions": {
                        "out_on_url": [
                        {
                            "index": 0,
                            "urls": [
                            "http://127.0.0.1/events/123456/on"
                            ],
                            "enabled": True
                        }
                        ],
                        "out_off_url": [
                        {
                            "index": 0,
                            "urls": [
                            "http://127.0.0.1/events/123456/off"
                            ],
                            "enabled": True
                        }
                        ],
                    }
                }
            )
    def mock_get(url):
        return MockResponse(url)
    class MockHttpResponse(object):
        def __init__(self,url) -> None:
            self.status =200
            self.url = url
    def mock_urlopen(url):
        MOCK_PARAMS.append(url)
        return MockHttpResponse(url)

    MOCK_PARAMS = []
    monkeypatch.setattr('socket.socket.__init__', MockSocket.__init__)
    monkeypatch.setattr('socket.socket.settimeout', mock_socket_settimeout)
    monkeypatch.setattr('socket.socket.connect_ex', mock_sock_connect_ex)
    monkeypatch.setattr(requests, 'get', mock_get)
    monkeypatch.setattr('urllib.request.urlopen', mock_urlopen)
    with app.app_context():
        testdevice = HWDevice(device_data)
        assert testdevice.setup_events() is True
    assert MOCK_PARAMS == [
        "http://127.0.0.1/settings/actions?index=0&name=out_on_url&enabled=true&urls[]=http://127.0.0.1/events/123456/on",
        "http://127.0.0.1/settings/actions?index=0&name=out_off_url&enabled=true&urls[]=http://127.0.0.1/events/123456/off",
    ]


def test_shelly1_setup_events_offline(monkeypatch, app):
    """ Tests event setup """
    class MockSocket(object):
        def __init__(self, family=-1, type=-1, proto=-1, fileno=None) -> None:
            pass

    def mock_socket_settimeout(self, timeout):
        return
    def mock_sock_connect_ex(self, target):
        return 1
    class MockResponse(object):
        def __init__(self, url) -> None:
            self.status_code = 500
            self.url = url
            self.text = 'ERROR'
    def mock_get(url):
        MOCK_PARAMS.append(url)
        return MockResponse(url)
    monkeypatch.setattr('socket.socket.__init__', MockSocket.__init__)
    monkeypatch.setattr('socket.socket.settimeout', mock_socket_settimeout)
    monkeypatch.setattr('socket.socket.connect_ex', mock_sock_connect_ex)
    monkeypatch.setattr(requests, 'get', mock_get)
    with app.app_context():
        testdevice = HWDevice(device_data)
        with pytest.raises(Exception):
            testdevice.setup_events()

def test_shelly1_setup_events_httperror(monkeypatch, app):
    """ Tests event setup """
    class MockSocket(object):
        def __init__(self, family=-1, type=-1, proto=-1, fileno=None) -> None:
            pass

    def mock_socket_settimeout(self, timeout):
        return
    def mock_sock_connect_ex(self, target):
        return 0
    class MockResponse(object):
        def __init__(self, url) -> None:
            self.status_code = 500
            self.url = url
            self.text = 'ERROR'
    def mock_get(url):
        MOCK_PARAMS.append(url)
        return MockResponse(url)
    monkeypatch.setattr('socket.socket.__init__', MockSocket.__init__)
    monkeypatch.setattr('socket.socket.settimeout', mock_socket_settimeout)
    monkeypatch.setattr('socket.socket.connect_ex', mock_sock_connect_ex)
    monkeypatch.setattr(requests, 'get', mock_get)
    with app.app_context():
        testdevice = HWDevice(device_data)
        with pytest.raises(Exception):
            testdevice.setup_events()

def test_shelly1_setup_events_httperror(monkeypatch, app):
    """ Tests event setup """
    class MockSocket(object):
        def __init__(self, family=-1, type=-1, proto=-1, fileno=None) -> None:
            pass

    def mock_socket_settimeout(self, timeout):
        return
    def mock_sock_connect_ex(self, target):
        return 0
    class MockResponse(object):
        def __init__(self, url) -> None:
            self.status_code = 500
            self.url = url
            self.text = 'ERROR'
    def mock_get(url):
        MOCK_PARAMS.append(url)
        return MockResponse(url)
    class MockHttpResponse(object):
        def __init__(self,url) -> None:
            self.status =500
            self.url = url
    def mock_urlopen(url):
        MOCK_PARAMS.append(url)
        return MockHttpResponse(url)
    monkeypatch.setattr('socket.socket.__init__', MockSocket.__init__)
    monkeypatch.setattr('socket.socket.settimeout', mock_socket_settimeout)
    monkeypatch.setattr('socket.socket.connect_ex', mock_sock_connect_ex)
    monkeypatch.setattr(requests, 'get', mock_get)
    monkeypatch.setattr('urllib.request.urlopen', mock_urlopen)
    with app.app_context():
        testdevice = HWDevice(device_data)
        with pytest.raises(Exception):
            testdevice.setup_events()

def test_shelly1_setup_events_verificationerror(monkeypatch, app):
    """ Tests event setup """
    class MockSocket(object):
        def __init__(self, family=-1, type=-1, proto=-1, fileno=None) -> None:
            pass

    def mock_socket_settimeout(self, timeout):
        return
    def mock_sock_connect_ex(self, target):
        return 0
    class MockResponse(object):
        def __init__(self, url) -> None:
            self.status_code = 500
            self.url = url
            self.text = json.dumps(
                {
                    "actions": {
                        "out_on_url": [
                        {
                            "index": 0,
                            "urls": [
                            "http://127.0.0.1/events/123456/on"
                            ],
                            "enabled": False
                        }
                        ],
                        "out_off_url": [
                        {
                            "index": 0,
                            "urls": [
                            "http://127.0.0.1/events/123456/off"
                            ],
                            "enabled": False
                        }
                        ],
                    }
                }
            )
    def mock_get(url):
        MOCK_PARAMS.append(url)
        return MockResponse(url)
    class MockHttpResponse(object):
        def __init__(self,url) -> None:
            self.status =200
            self.url = url
    def mock_urlopen(url):
        MOCK_PARAMS.append(url)
        return MockHttpResponse(url)
    monkeypatch.setattr('socket.socket.__init__', MockSocket.__init__)
    monkeypatch.setattr('socket.socket.settimeout', mock_socket_settimeout)
    monkeypatch.setattr('socket.socket.connect_ex', mock_sock_connect_ex)
    monkeypatch.setattr(requests, 'get', mock_get)
    monkeypatch.setattr('urllib.request.urlopen', mock_urlopen)
    with app.app_context():
        testdevice = HWDevice(device_data)
        with pytest.raises(Exception):
            testdevice.setup_events()
