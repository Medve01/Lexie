import json

from flask import Blueprint, request
from flask.json import jsonify

from lexie.devices.LexieDevice import LexieDevice, LexieDeviceType

api_bp = Blueprint('device_api', __name__, url_prefix='/api')

@api_bp.route('/device', methods=["PUT"])
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

@api_bp.route('/device/<device_id>', methods=['GET'])
def device_get(device_id: str):
    """ returns LexieDevice status in"""
    device = LexieDevice(device_id=device_id)
    return jsonify(device.to_dict())

@api_bp.route('/device/<device_id>/<command>', methods=['GET'])
def device_command(device_id: str, command: str):
    """ issues a command to the device """
    device = LexieDevice(device_id)
    valid_commands = [
        "on",
        "off",
        "toggle",
    ]
    if command not in valid_commands:
        response = {"Error:": "Invalid command"}
    if command == "on":
        response = device.relay_action_set(True)
    elif command == "off":
        response = device.relay_action_set(False)
    elif command == "toggle":
        response = device.relay_action_toggle()
    return jsonify(response)
