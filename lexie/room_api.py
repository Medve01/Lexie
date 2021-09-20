import json

from flask import Blueprint, request
from flask.json import jsonify

from lexie.smarthome.Room import Room

room_api_bp = Blueprint('room_api', __name__, url_prefix='/api/room')

@room_api_bp.route('/', methods=['GET'])
def room_get_all():
    """ returns all rooms """
    return_rooms = []
    rooms = Room.get_all_rooms()
    for room in rooms:
        return_rooms.append(room.to_dict())
    return jsonify(return_rooms)

@room_api_bp.route('/<room_id>', methods=['GET'])
def room_get(room_id: str):
    """ returns room by id """
    room = Room(room_id=room_id)
    return jsonify(room.to_dict())

@room_api_bp.route('/', methods=["PUT"])
def device_new():
    """ creates a new device in database """
    room_data = json.loads(request.data)
    room = Room.new(
        room_name=room_data['room_name']
    )
    return jsonify(room.to_dict())

@room_api_bp.route('/<room_id>', methods=['DELETE']) #pragma: nocover
def room_delete(room_id: str): #pylint: disable=unused-argument #pragma: nocover
    """ deletes a room """ #pragma: nocover
    return jsonify('Not yet implemented') #pragma: nocover
