from flask import Blueprint
from flask.json import jsonify

from lexie.devices.device import LexieDevice

api_bp = Blueprint('device_api', __name__, url_prefix='/api')

@api_bp.route('/device/<device_id>')
def device_status(device_id: str):
    """ returns LexieDevice status in"""
    device = LexieDevice(device_id=device_id)
    return jsonify(device.to_dict())
