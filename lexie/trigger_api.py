from flask import Blueprint, request
from flask.json import jsonify

from lexie.apikey import check_apikey
from lexie.smarthome import exceptions, routine

trigger_api_bp = Blueprint('trigger_api', __name__, url_prefix='/api/trigger')

@trigger_api_bp.before_request
def validate_api_key():
    """ checks if client sent a valid api key, or has a valid session """
    sent_api_key = request.headers.get('X-API-KEY')
    if sent_api_key is None or not check_apikey(sent_api_key):
        return jsonify({'Error': 'Authentication error'}), 403
    return None

@trigger_api_bp.route('/', methods=['GET'])
def trigger_get_all():
    """ returns all triggers """
    return_triggers = []
    triggers = routine.Trigger.get_all()
    for trigger in triggers:
        return_triggers.append(trigger.trigger_dict)
    return jsonify(return_triggers)

@trigger_api_bp.route('/<trigger_id>', methods=['GET'])
def trigger_get(trigger_id: str):
    """ returns trigger by id """
    try:
        trigger = routine.Trigger(trigger_id)
        return jsonify(trigger.trigger_dict)
    except exceptions.NotFoundException:
        return jsonify({'error': 'Room not found'}), 404

@trigger_api_bp.route('/<trigger_id>', methods=['DELETE'])
def trigger_delete(trigger_id: str): #pylint: disable=unused-argument
    """ deletes a a trigger and the full chain of steps if exists """
    try:
        trigger = routine.Trigger(trigger_id)
        trigger.delete()
    except exceptions.NotFoundException: #pylint: disable=bare-except
        return jsonify({'error': f"Trigger not found with id {trigger_id}"}), 404
    return jsonify(f'Trigger {trigger_id} deleted.')
