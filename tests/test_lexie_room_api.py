import json
from typing import Any
import pytest
from lexie.app import create_app
from lexie.db import init__db
from lexie.smarthome.Room import Room

test_room_data = {
                "room_id": "1234",
                "room_name": "Mock room",
            }

class MockRoom: #pylint: disable=too-few-public-methods
    """ mocks LexieDevice so we can test the http endpoint only """
    def __init__(self, room_id): #pylint: disable=redefined-outer-name
        """ constructor """
        self.id = room_id
        self.name = test_room_data['room_name']

    def to_dict(self):
        temp_self = {
            'room_id': self.id,
            'room_name': self.name,
        }
        return temp_self

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

def test_room_api_get_room(monkeypatch, client):
    """" tests /api/room/room_id"""
    def mockroom_init(Any, room_id):
        return MockRoom(room_id)
    
    def mockroom_to_dict(Any):
        mock_room = MockRoom('1234')
        return mock_room.to_dict()
    monkeypatch.setattr('lexie.smarthome.Room.Room.__init__', MockRoom.__init__)
    monkeypatch.setattr('lexie.smarthome.Room.Room.to_dict', mockroom_to_dict)
    res = client.get('/api/room/12534')

    assert json.loads(res.data) == {
        'room_id': '1234',
        'room_name': 'Mock room'
        }

def test_room_api_get_all_rooms(monkeypatch, client):
    """ tests /api/device """
    def mock_get_all_rooms():
        all_rooms = []
        all_rooms.append(MockRoom('1234'))
        all_rooms.append(MockRoom('4321'))
        return all_rooms

    monkeypatch.setattr('lexie.smarthome.Room.Room.__init__', MockRoom.__init__)
    monkeypatch.setattr('lexie.smarthome.Room.Room.get_all_rooms', mock_get_all_rooms)
    res = client.get('/api/room/')
    assert json.loads(res.data) == [
        {
            'room_id': '1234',
            'room_name': 'Mock room',
        },
        {
            'room_id': '4321',
            'room_name': 'Mock room',
        },
    ]

def test_room_api_new_room(monkeypatch, client):
    """ tests PUT /api/device/6666 """
    def mock_new_room(room_name):
        return MockRoom(room_id='9999')
    
    monkeypatch.setattr('lexie.smarthome.Room.Room.new', mock_new_room)
    res = client.put('/api/room/', data=json.dumps(test_room_data))
    assert json.loads(res.data) == {
                                        "room_id": "9999",
                                        "room_name": "Mock room",
                                    }
