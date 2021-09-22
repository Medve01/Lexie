import pytest

from tests.fixtures.test_flask_app import app, client


def test_event_hook(client):
    """tests default page"""
    res = client.get('/events/1234/switched_on')
    assert res.json == 'Event received.'