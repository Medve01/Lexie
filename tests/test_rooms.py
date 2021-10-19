import pytest

from lexie.smarthome.models import db as sqla_db
from lexie.smarthome.room import Room
from lexie.smarthome.lexiedevice import LexieDevice
from tests.fixtures.test_flask_app import app


def test_room_existing(app):
    with app.app_context():
        result = Room('1234')
    assert result.name == 'Test room 1'

def test_room_nonexisting(app):
    with app.app_context():
        with pytest.raises(Exception):
            Room('666')

def test_room_to_dict(app):
    with app.app_context():
        room = Room('1234')
    assert room.to_dict() == {
        'room_name': 'Test room 1',
        'room_id': '1234'
    }

def test_room_new(app):
    with app.app_context():
        room = Room.new('Garbage container')
    assert isinstance(room, Room)
    assert room.name == 'Garbage container'

def test_get_all_rooms(app):
    with app.app_context():
        rooms = Room.get_all_rooms()
    for room in rooms:
        assert isinstance(room, Room)

def test_room_delete(app):
    with app.app_context():
        room = Room.new("Test room for delete test")
        room_id = room.id
        room = Room(room_id=room_id)
        room.delete()
        with pytest.raises(Exception):
            Room(room_id=room_id)


def test_room_delete_with_devices(app):
    with app.app_context():
        room = Room.new("Test room for delete test")
        room_id = room.id
        device = LexieDevice('1234')
        device.move(room)
        room = Room(room_id=room_id)
        room.delete()
        with pytest.raises(Exception):
            Room(room_id=room_id)
        device = LexieDevice('1234')
        assert device.room.id is None
