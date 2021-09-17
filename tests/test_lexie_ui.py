import pytest

from urllib.parse import urlparse
from typing import Any

from lexie.lexie_app import create_app
from lexie.db import init__db

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