import pytest

from typing import Any
import pytest
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

def test_ui_dashboard(client):
    """tests default page"""
    res = client.get('/ui/')
    assert res.status_code == 200

def test_ui_404(client):
    """ tests page not found """
    res = client.get('/ui/szlartibartfaszt')
    assert res.status_code == 404