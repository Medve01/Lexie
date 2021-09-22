from shortuuid import uuid  # type: ignore # pylint:disable=import-error

from .models import Room as room_model
from .models import db


class Room:
    """ Represents a room in a smart home """
    def __init__(self, room_id: str) -> None:
        room = room_model.query.filter_by(id=room_id).first()
        if room is None:
            raise Exception(f'Room with id {room_id} does not exist')
        self.name = room.name
        self.id = room.id # pylint: disable=invalid-name

    def to_dict(self):
        """ returns a dict representaion of the object """
        temp_self = {
            'room_id': self.id,
            'room_name': self.name,
        }
        return temp_self

    def delete(self) -> None:
        """" deletes the room from database """
        room = room_model.query.filter_by(id=self.id).first()
        try:
            db.session.delete(room)
            db.session.commit()
        except: #pragma: nocover
            raise Exception('Error during room delete from database') #pylint: disable=raise-missing-from #pragma: nocover



    @staticmethod
    def new(room_name:str):

        """ Static method to store a new room in database.
        room_name is mandatory """
        room_id = uuid()
        room = room_model(id=room_id, name = room_name)
        try:
            db.session.add(room)
            db.session.commit()
        except Exception: # pragma: nocover
            print('Database error')
            raise
        return Room(room_id = room_id)

    @staticmethod
    def get_all_rooms():
        """ returns a list(Room) of all rooms in database"""
        rooms = []
        results = room_model.query.all()
        for result in results:
            rooms.append(Room(result.id))
        return rooms
