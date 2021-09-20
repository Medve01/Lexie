from flask import current_app as app
from shortuuid import uuid  # type: ignore # pylint:disable=import-error

from lexie.db import get_db


class Room:
    """ Represents a room in a smart home """
    def __init__(self, room_id: str) -> None:
        with app.app_context():
            lexie_db = get_db()
            room = lexie_db.execute(
                "select room_name from room where room_id=?",
                (room_id,)
            ).fetchone()
            if room is None:
                raise Exception(f"Invalid device type: {room_id}") # pragma: nocover
            self.id = room_id # pylint:disable=invalid-name
            self.name = room['room_name']


    def to_dict(self):
        """ returns a dict representaion of the object """
        temp_self = {
            'room_id': self.id,
            'room_name': self.name,
        }
        return temp_self

    @staticmethod
    def new(room_name:str):

        """ Static method to store a new room in database.
        room_name is mandatory """
        room_id = uuid()
        with app.app_context():
            lexie_db = get_db()
            try:
                lexie_db.execute(
                    "INSERT INTO room (room_id, room_name) values (?, ?)",
                    (room_id, room_name)
                )
                lexie_db.commit()
            except Exception: # pragma: nocover
                print('Database error')
                raise
            return Room(room_id = room_id)

    @staticmethod
    def get_all_rooms():
        """ returns a list(Room) of all rooms in database"""
        rooms = []
        with app.app_context():
            lexie_db = get_db()
            db_rooms = lexie_db.execute(
                "select room_id from room"
            ).fetchall()
            if db_rooms is None:
                raise Exception("Error fetching rooms from database: none returned. DB empty?") #pragma: nocover
            for db_room in db_rooms:
                rooms.append(Room(db_room['room_id']))
        return rooms
