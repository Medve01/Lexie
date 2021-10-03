# Flask modules
import logging

from flask import Blueprint
from flask.json import jsonify

from lexie.app import socketio  # pylint: disable=cyclic-import
from lexie.smarthome.exceptions import InvalidEventException, NotFoundException
from lexie.smarthome.LexieDevice import LexieDevice

# Register blueprint
events_bp = Blueprint('events', __name__, url_prefix='/events')


def handle_event(device_id, event: str):
    """ handles the event """
    socketio.emit('event', {'device_id': device_id, 'event': event})
    logging.info("Device: %s just sent an event: %s", device_id, event)
    device = LexieDevice(device_id=device_id)
    if event == "on":
        device.set_status('ison', True)
    elif event == "off":
        device.set_status('ison', False)
    else:
        raise InvalidEventException
    return jsonify("Event received.")

@events_bp.route('/<device_id>/<event>')
def event_incoming(device_id:str, event: str):
    """ handles incoming events from any device that handles it. Mostly designed for Shelly """
    try:
        handle_event(device_id=device_id, event=event)
    except NotFoundException:
        return jsonify({'error': f'Device not found with id: {device_id}'}), 404
    except InvalidEventException:
        return jsonify({'error': 'Invalid event.'}), 400
    return jsonify("Event received.")
