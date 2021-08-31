from lexie.app import create_app
import pytest

@pytest.fixture
def app():
    _app = create_app()
    return _app

@pytest.fixture
def client(app):
    _client = app.test_client()
    return _client

def test_server_up(client):
    res = client.get('/')
    assert res.status_code == 200

def test_default_page(client):
    res = client.get('/')
    assert b'Hello World!' in res.data