import json

from flask import Blueprint, current_app, request
from flask.json import jsonify
from flask_login import current_user

from lexie.authentication import check_apikey
from lexie.smarthome import exceptions
from lexie.smarthome.exceptions import NotFoundException
from lexie.smarthome.lexiedevice import (LexieDevice, LexieDeviceType,
                                         get_all_devices,
                                         get_all_devices_with_rooms)

device_api_bp = Blueprint('device_api', __name__, url_prefix='/api/device')

@device_api_bp.before_request
def validate_api_key():
    """ if there's no login in session, checks if client sent a valid api key, or has a valid session """
    if not current_user.is_authenticated:
        sent_api_key = request.headers.get('X-API-KEY')
        if sent_api_key is None or not check_apikey(sent_api_key):
            return jsonify({'Error': 'Authentication error'}), 403
    return None

@device_api_bp.route('/', methods=["PUT"])
def device_new():
    """ creates a new device in database """
    device_data = json.loads(request.data)
    device = LexieDevice.new(
        device_name=device_data['device_name'],
        device_type=LexieDeviceType(int(device_data['device_type'])),
        device_manufacturer=device_data['device_manufacturer'],
        device_product=device_data['device_product'],
        device_attributes=device_data['device_attributes']
    )
    return jsonify(device.to_dict())

@device_api_bp.route('/<device_id>', methods=['GET'])
def device_get(device_id: str):
    """ returns LexieDevice status in"""
    try:
        device = LexieDevice(device_id=device_id)
        return jsonify(device.to_dict())
    except exceptions.NotFoundException:
        return jsonify({'error': f'Device not found with id: {device_id}'}), 404

@device_api_bp.route('/<device_id>/<command>', methods=['GET'])
def device_command(device_id: str, command: str):
    """ issues a command to the device """
    try:
        device = LexieDevice(device_id)
    except exceptions.NotFoundException:
        return jsonify({'error': f'Device not found with id: {device_id}'}), 404
    valid_commands = [
        "on",
        "off",
        "toggle",
    ]
    if device.supports_events:
        valid_commands.append("setup-events")
    if command not in valid_commands:
        response = {"Error:": "Invalid command"}
    elif command == "on":
        response = device.action_turn(True)
    elif command == "off":
        response = device.action_turn(False)
    elif command == "toggle":
        response = device.action_toggle()
    elif command == "setup-events":
        current_app.logger.debug('Calling LexieDevice.setup_events()')
        device.setup_events()
        response = {"Result": "Success"}
    return jsonify(response)

@device_api_bp.route('/', methods=['GET'])
def device_get_all():
    """ returns all devices """
    if request.args.get('groupby') == 'rooms':
        response = get_all_devices_with_rooms()
    else:
        response = []
        devices = get_all_devices()
        for device in devices:
            response.append(device.to_dict())
    return jsonify(response)

@device_api_bp.route('/<device_id>', methods=['DELETE'])
def device_delete(device_id: str):
    """ deletes a device """
    try:
        device = LexieDevice(device_id=device_id)
    except NotFoundException:
        return jsonify({'error': 'device not found'}), 404
    device.delete()
    return jsonify('Success')
