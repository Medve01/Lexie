from __future__ import annotations

from typing import Any

from flask_sqlalchemy import DefaultMeta, SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()
BaseModel: DefaultMeta = db.Model

class Room(BaseModel): #pylint: disable=too-few-public-methods # type: ignore
    """ Database model for Rooms in a smart home """
    id = db.Column(db.String(22), primary_key = True) # pylint: disable=invalid-name
    name = db.Column(db.String(50), nullable=False)

class DeviceType(BaseModel): #pylint: disable=too-few-public-methods # type: ignore
    """ Database model for Device Types """
    id = db.Column(db.Integer, primary_key=True) # pylint: disable=invalid-name
    name = db.Column(db.String(50), nullable=False)
    actions = db.Column(db.TEXT, nullable=True)

class Device(BaseModel): #pylint: disable=too-few-public-methods # type: ignore
    """ Database model for Devices """
    id = db.Column(db.String(22), primary_key=True) # pylint: disable=invalid-name
    name = db.Column(db.String(50), nullable=False)
    device_type = db.Column(db.Integer, db.ForeignKey('device_type.id'), nullable=False)
    devicetype: Any = relationship(DeviceType)
    manufacturer = db.Column(db.String(20), nullable=False)
    product = db.Column(db.String(20), nullable=False)
    attributes = db.Column(db.TEXT, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)
    room: Any = relationship(Room)
