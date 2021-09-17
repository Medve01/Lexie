# Flask modules
import logging

from flask import Blueprint
from flask.json import jsonify

# Register blueprint
events_bp = Blueprint('events', __name__, url_prefix='/events')

@events_bp.route('/<device_id>/<event>')
def event_incoming(device_id:str, event: str):
    """ handles incoming events from any device that handles it. Mostly designed for Shelly """
    logging.info("Device: %s just sent an event: %s", device_id, event)
    return jsonify("Event received.")
