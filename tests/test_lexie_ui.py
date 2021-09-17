import pytest

from urllib.parse import urlparse
from typing import Any

from lexie.lexie_app import create_app
from lexie.db import init__db
from lexie.views import get_drivers
from lexie.devices.LexieDevice import LexieDeviceType

@pytest.fixture
def app():
    _app = create_app(testing=True)
    with _app.app_context():
        init__db()
    return _app


@pytest.fixture
def client(app):
    _client = app.test_client()
    return _client

def mock_os_listdir(directory):
    if directory=='./drivers':
        return [
            '__init__.py',
            'shelly',
            'xiaomi'
        ]
    if directory=='./drivers/shelly':
        return [
                'shelly1.py',
                'shelly_motion.py'
            ]
    if directory=='./drivers/xiaomi':
        return ['dreamemoppro.py']

def test_default_page(client):
    """tests default page"""
    res = client.get('/')
    assert res.status_code == 302
    parsed_response_url = urlparse(res.location)
    assert parsed_response_url.path == '/ui'

def test_ui_dashboard(client):
    """tests default page"""
    res = client.get('/ui/')
    assert res.status_code == 200

def test_ui_404(client):
    """ tests page not found """
    res = client.get('/ui/szlartibartfaszt')
    assert res.status_code == 404

def test_ui_views_get_drivers(monkeypatch):

    monkeypatch.setattr('os.listdir', mock_os_listdir)
    result = get_drivers()
    assert result == [
        'shelly - shelly1',
        'shelly - shelly_motion',
        'xiaomi - dreamemoppro'
    ]

def test_add_device_get(monkeypatch,client):
    monkeypatch.setattr('os.listdir', mock_os_listdir)
    result=client.get('/ui/add-device')
    assert result.status_code == 200

def test_add_device_post(monkeypatch, client):
    def mock_lexiedevice_new(**kwargs):
        global passed_arguments_to_mock
        passed_arguments_to_mock = kwargs
        return "666666"
    monkeypatch.setattr('lexie.devices.LexieDevice.LexieDevice.new', mock_lexiedevice_new)
    result = client.post('/ui/add-device', data={
        #         device_name=device_data['device_name'],
        # device_type=LexieDeviceType(device_data['device_type']),
        # device_manufacturer=device_data['device_driver'].split('-')[0].strip(),
        # device_product=device_data['device_driver'].split('-')[1].strip(),
        # device_attributes={'ip_address': device_data['device_ip']}
        'device_name': 'Test device',
        'device_type': 1,
        'device_driver': 'shelly - shelly1',
        'device_ip': '127.0.0.1'
    })
    assert result.status_code == 302
    assert (passed_arguments_to_mock['device_name'] == 'Test device' and
        isinstance(passed_arguments_to_mock['device_type'], LexieDeviceType) and
        passed_arguments_to_mock['device_manufacturer'] == 'shelly' and
        passed_arguments_to_mock['device_product'] == 'shelly1' and
        passed_arguments_to_mock['device_attributes'] == {'ip_address': '127.0.0.1'}
    )
