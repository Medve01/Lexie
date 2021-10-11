

class NotFoundException(Exception):
    """ to be thrown when an object (Room, Device, etc)
        is not found in the database"""

class InvalidEventException(Exception):
    """ to raise if a url was hit with an undefined event """
