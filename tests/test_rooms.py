import pytest
from lexie.app import create_app
from lexie.db import init__db
from lexie.smarthome.Room import Room

@pytest.fixture
def app():
    _app = create_app(testing=True)
    with _app.app_context():
        init__db()
    return _app

def test_room_existing(app):
    with app.app_context():
        result = Room('1234')
    assert result.name == 'Living room'

def test_room_nonexisting(app):
    with app.app_context():
        with pytest.raises(Exception):
            Room('666')

def test_room_to_dict(app):
    with app.app_context():
        room = Room('1234')
    assert room.to_dict() == {
        'room_name': 'Living room',
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
    assert len(rooms) == 2
    assert isinstance(rooms[0], Room) and isinstance(rooms[1], Room)