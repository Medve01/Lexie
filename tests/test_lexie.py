import json
import pytest
from lexie.app import create_app
from lexie.db import init__db

@pytest.fixture
def app():
    _app = create_app()
    with _app.app_context():
        init__db()
    return _app


@pytest.fixture
def client(app):
    _client = app.test_client()
    return _client

def test_server_up(client):
    """ tests if server started successfully """
    res = client.get('/')
    assert res.status_code == 200

def test_default_page(client):
    """tests default page"""
    res = client.get('/')
    assert b'Nothing to see here - yet.' in res.data

def test_get_device(client):
    """" tests /api/device/device_id"""
    res = client.get('/api/device/1234')
    assert res.data == b'{"device_id":"1234","device_name":"Test device","device_type":{"devicetype_id":1,"devicetype_name":"Test devicetype"}}\n' # pylint:disable=line-too-long
