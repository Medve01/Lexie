from flask import Blueprint
from flask.json import jsonify

from lexie.smarthome import Routine, exceptions

trigger_api_bp = Blueprint('trigger_api', __name__, url_prefix='/api/trigger')

@trigger_api_bp.route('/', methods=['GET'])
def trigger_get_all():
    """ returns all triggers """
    return_triggers = []
    triggers = Routine.Trigger.get_all()
    for trigger in triggers:
        return_triggers.append(trigger.trigger_dict)
    return jsonify(return_triggers)

@trigger_api_bp.route('/<trigger_id>', methods=['GET'])
def trigger_get(trigger_id: str):
    """ returns trigger by id """
    try:
        trigger = Routine.Trigger(trigger_id)
        return jsonify(trigger.trigger_dict)
    except exceptions.NotFoundException:
        return jsonify({'error': 'Room not found'}), 404

@trigger_api_bp.route('/<trigger_id>', methods=['DELETE'])
def trigger_delete(trigger_id: str): #pylint: disable=unused-argument
    """ deletes a a trigger and the full chain of steps if exists """
    try:
        trigger = Routine.Trigger(trigger_id)
        trigger.delete()
    except exceptions.NotFoundException: #pylint: disable=bare-except
        return jsonify({'error': f"Trigger not found with id {trigger_id}"}), 404
    return jsonify(f'Trigger {trigger_id} deleted.')
