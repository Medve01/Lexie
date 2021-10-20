from flask import Blueprint, request
from flask.json import jsonify

from lexie.apikey import check_apikey
from lexie.smarthome import exceptions, routine

step_api_bp = Blueprint('step_api', __name__, url_prefix='/api/step')

@step_api_bp.before_request
def validate_api_key():
    """ checks if client sent a valid api key, or has a valid session """
    sent_api_key = request.headers.get('X-API-KEY')
    if sent_api_key is None or not check_apikey(sent_api_key):
        return jsonify({'Error': 'Authentication error'}), 403
    return None

@step_api_bp.route('/<step_id>', methods=['GET'])
def step_get(step_id: str):
    """ returns step by id """
    try:
        step = routine.Step(step_id)
        return jsonify(step.step_dict)
    except exceptions.NotFoundException:
        return jsonify({'error': 'Step not found'}), 404

@step_api_bp.route('/<step_id>', methods=['DELETE'])
def step_delete(step_id: str): #pylint: disable=unused-argument
    """ removes a step from the chain """
    try:
        step = routine.Step(step_id)
        step.delete()
    except exceptions.NotFoundException: #pylint: disable=bare-except
        return jsonify({'error': f"Step not found with id {step_id}"}), 404
    return jsonify(f'Trigger {step_id} deleted.')
