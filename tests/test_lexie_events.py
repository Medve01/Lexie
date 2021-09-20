import pytest
from lexie.app import create_app
from lexie.db import init__db

@pytest.fixture
def lexie_app():
    """ creates a Lexie app instance """
    _app = create_app(testing=True)
    with _app.app_context():
        init__db()
    return _app


@pytest.fixture
def lexie_client(lexie_app):
    """ creates a Lexie app client """
    _client = lexie_app.test_client()
    return _client

def test_event_hook(lexie_client):
    """tests default page"""
    res = lexie_client.get('/events/1234/switched_on')
    assert res.json == 'Event received.'