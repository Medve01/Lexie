import json
from typing import Any

import pytest

from lexie.smarthome.room import Room
from lexie.smarthome import exceptions
from tests.fixtures.test_flask_app import app, api_client as client, noauth_client

test_room_data = {
                "room_id": "1234",
                "room_name": "Mock room",
            }

class MockRoom: #pylint: disable=too-few-public-methods
    """ mocks Room so we can test the http endpoint only """
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

def test_api_get_room_noauth(noauth_client):
    res = noauth_client.get('/api/room/1234')
    assert res.status_code == 403

def test_room_api_get_room(monkeypatch, client):
    """" tests /api/room/room_id"""
    def mockroom_init(Any, room_id):
        return MockRoom(room_id)
    
    def mockroom_to_dict(Any):
        mock_room = MockRoom('1234')
        return mock_room.to_dict()
    monkeypatch.setattr('lexie.smarthome.room.Room.__init__', MockRoom.__init__)
    monkeypatch.setattr('lexie.smarthome.room.Room.to_dict', mockroom_to_dict)
    res = client.get('/api/room/12534')

    assert json.loads(res.data) == {
        'room_id': '1234',
        'room_name': 'Mock room'
        }

def test_room_api_get_room_nonexisting(monkeypatch, client):
    """" tests /api/room/room_id"""
    def mockroom_init(Any, room_id):
        raise exceptions.NotFoundException
    
    def mockroom_to_dict(Any):
        mock_room = MockRoom('1234')
        return mock_room.to_dict()
    monkeypatch.setattr('lexie.smarthome.room.Room.__init__', mockroom_init)
    monkeypatch.setattr('lexie.smarthome.room.Room.to_dict', mockroom_to_dict)
    res = client.get('/api/room/12534')

    assert res.status_code == 404

def test_room_api_get_all_rooms(monkeypatch, client):
    """ tests /api/device """
    def mock_get_all_rooms():
        all_rooms = []
        all_rooms.append(MockRoom('1234'))
        all_rooms.append(MockRoom('4321'))
        return all_rooms

    monkeypatch.setattr('lexie.smarthome.room.Room.__init__', MockRoom.__init__)
    monkeypatch.setattr('lexie.smarthome.room.Room.get_all_rooms', mock_get_all_rooms)
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
    
    monkeypatch.setattr('lexie.smarthome.room.Room.new', mock_new_room)
    res = client.put('/api/room/', data=json.dumps(test_room_data))
    assert json.loads(res.data) == {
                                        "room_id": "9999",
                                        "room_name": "Mock room",
                                    }

def test_room_api_delete(monkeypatch, client):
    """ tests DELETE /api/device/6666 """
    def mock_delete_room(room_id):
        return

    monkeypatch.setattr('lexie.smarthome.room.Room.delete', mock_delete_room)
    monkeypatch.setattr('lexie.smarthome.room.Room.__init__', MockRoom.__init__)

    res = client.delete('/api/room/1234')
    assert json.loads(res.data) == 'Room 1234 deleted.'

def test_room_api_delete_nonexisting(monkeypatch, client):
    """ tests DELETE /api/device/6666 """
    def mock_delete_room(room_id):
        raise exceptions.NotFoundException

    monkeypatch.setattr('lexie.smarthome.room.Room.delete', mock_delete_room)
    monkeypatch.setattr('lexie.smarthome.room.Room.__init__', MockRoom.__init__)

    res = client.delete('/api/room/1234')
    assert res.status_code == 404
