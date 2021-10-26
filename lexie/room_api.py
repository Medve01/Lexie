import json

from flask import Blueprint, request
from flask.json import jsonify
from flask_login import current_user

from lexie.authentication import check_apikey
from lexie.smarthome import exceptions
from lexie.smarthome.room import Room

room_api_bp = Blueprint('room_api', __name__, url_prefix='/api/room')

@room_api_bp.before_request
def validate_api_key():
    """ if there's no login in session, checks if client sent a valid api key, or has a valid session """
    if not current_user.is_authenticated:
        sent_api_key = request.headers.get('X-API-KEY')
        if sent_api_key is None or not check_apikey(sent_api_key):
            return jsonify({'Error': 'Authentication error'}), 403
    return None

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
    try:
        room = Room(room_id=room_id)
        return jsonify(room.to_dict())
    except exceptions.NotFoundException:
        return jsonify({'error': 'Room not found'}), 404

@room_api_bp.route('/', methods=["PUT"])
def room_new():
    """ creates a new device in database """
    room_data = json.loads(request.data)
    room = Room.new(
        room_name=room_data['room_name']
    )
    return jsonify(room.to_dict())

@room_api_bp.route('/<room_id>', methods=['DELETE'])
def room_delete(room_id: str): #pylint: disable=unused-argument
    """ deletes a room """
    try:
        room = Room(room_id=room_id)
        room.delete()
    except exceptions.NotFoundException: #pylint: disable=bare-except
        return jsonify({'error': f"Room not found with id {room_id}"}), 404
    return jsonify(f'Room {room_id} deleted.')
