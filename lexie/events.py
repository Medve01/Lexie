# Flask modules
import logging

from flask import Blueprint, make_response
from flask.json import jsonify

from lexie.app import socketio  # pylint: disable=cyclic-import
from lexie.smarthome.LexieDevice import LexieDevice

# Register blueprint
events_bp = Blueprint('events', __name__, url_prefix='/events')

@events_bp.route('/<device_id>/<event>')
def event_incoming(device_id:str, event: str):
    """ handles incoming events from any device that handles it. Mostly designed for Shelly """
    socketio.emit('event', {'device_id': device_id, 'event': event})
    logging.info("Device: %s just sent an event: %s", device_id, event)
    try:
        device = LexieDevice(device_id=device_id)
    except Exception: # pylint: disable=broad-except
        return make_response(jsonify({'Error': 'Device not found with id: ' + device_id}), 404)
    if event == "on":
        device.set_status('ison', True)
    elif event == "off":
        device.set_status('ison', False)
    else:
        return make_response(jsonify({"Error": "Invalid event sent"}), 400)
    return jsonify("Event received.")
