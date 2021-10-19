# Flask modules
import logging

from flask import Blueprint
from flask.json import jsonify

from lexie.smarthome.events import send_event
from lexie.smarthome.exceptions import InvalidEventException, NotFoundException
from lexie.smarthome.lexiedevice import LexieDevice
from lexie.smarthome import eventlog

# Register blueprint
events_bp = Blueprint('events', __name__, url_prefix='/events')

VALID_EVENTS= ['on', 'off']

def handle_event(device_id, event: str):
    """ handles the event """
    logging.info("Device: %s just sent an event: %s", device_id, event)
    device = LexieDevice(device_id=device_id)
    if event not in VALID_EVENTS:
        raise InvalidEventException
    send_event(device.device_id, event, event_type='status')
    eventlog.log(f'Event received from {device.device_name}: {event}')
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
