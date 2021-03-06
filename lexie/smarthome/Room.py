from shortuuid import uuid  # type: ignore # pylint:disable=import-error

from lexie.smarthome import exceptions, models


class Room:
    """ Represents a room in a smart home """
    def __init__(self, room_id: str = None) -> None:
        if room_id is None:
            self.id = None # pylint: disable=invalid-name
            self.name = 'Unassigned'
        else:
            room = models.Room.query.filter_by(id=room_id).first()
            if room is None:
                # raise Exception(f'Room with id {room_id} does not exist')
                raise exceptions.NotFoundException(f'Room ({room_id} does not exist')
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
        if self.id is not None:
            # check if there are devices in the room. If yes, set room_id to null
            devices = models.Device.query.filter_by(room_id = self.id).all()
            if devices is not None:
                for device in devices:
                    device.room_id = None
                models.db.session.commit()
            room = models.Room.query.filter_by(id=self.id).first()
            try:
                models.db.session.delete(room)
                models.db.session.commit()
            except: #pragma: nocover
                raise Exception('Error during room delete from database') #pylint: disable=raise-missing-from #pragma: nocover



    @staticmethod
    def new(room_name:str):

        """ Static method to store a new room in database.
        room_name is mandatory """
        room_id = uuid()
        room = models.Room(id=room_id, name = room_name)
        try:
            models.db.session.add(room)
            models.db.session.commit()
        except Exception: # pragma: nocover
            print('Database error')
            raise
        return Room(room_id = room_id)

    @staticmethod
    def get_all_rooms():
        """ returns a list(Room) of all rooms in database"""
        rooms = []
        results = models.Room.query.all()
        for result in results:
            rooms.append(Room(result.id))
        # check if we have devices not assigned to a room
        results = models.db.session.query(models.Device).filter(models.Device.room_id == None).count() # pylint: disable=singleton-comparison
        if results > 0:
            rooms.append(Room())
        return rooms
