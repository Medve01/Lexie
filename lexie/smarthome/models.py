from __future__ import annotations

import json
from typing import Any

from flask_sqlalchemy import DefaultMeta, SQLAlchemy
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import relationship

db = SQLAlchemy()
BaseModel: DefaultMeta = db.Model

class Event(BaseModel): #pylint: disable=too-few-public-methods # type: ignore
    """ represents an event in the database"""
    __bind_key__ = "events"
    id = db.Column(db.Integer, primary_key = True) # pylint: disable=invalid-name
    device_id = db.Column(db.String(22), nullable=False)
    event = db.Column(db.TEXT, nullable=False)

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

def prepare_db() -> None:
    """ if database found empty, this creates an empty structure and some system data in it """
    db.create_all() # pragma: nocover
    db.session.query(Event).delete() # pragma: nocover
    db.session.commit() # pragma: nocover
    try: # pragma: nocover
        db.engine.execute("select * from device_type") # pragma: nocover
    except OperationalError: # pragma: nocover
        db.session.add(DeviceType( # pragma: nocover
            id=1,
            name='Relay',
            actions=json.dumps([{"name": "onoff", "icon": "fa fa-toggle-on"}, {"name": "toggle", "icon": "fas fa-bullseye"}])
        ))
        db.session.add(DeviceType( # pragma: nocover
            id=2,
            name='Light',
            actions=json.dumps([{"name": "onoff", "icon": "fa fa-toggle-on"}, {"name": "toggle", "icon": "fas fa-bullseye"}])
        ))
        db.session.commit() # pragma: nocover
