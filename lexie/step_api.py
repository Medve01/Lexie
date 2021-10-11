from flask import Blueprint
from flask.json import jsonify

from lexie.smarthome import Routine, exceptions

step_api_bp = Blueprint('step_api', __name__, url_prefix='/api/step')

@step_api_bp.route('/<step_id>', methods=['GET'])
def step_get(step_id: str):
    """ returns step by id """
    try:
        step = Routine.Step(step_id)
        return jsonify(step.step_dict)
    except exceptions.NotFoundException:
        return jsonify({'error': 'Step not found'}), 404

@step_api_bp.route('/<step_id>', methods=['DELETE'])
def step_delete(step_id: str): #pylint: disable=unused-argument
    """ removes a step from the chain """
    try:
        step = Routine.Step(step_id)
        step.delete()
    except exceptions.NotFoundException: #pylint: disable=bare-except
        return jsonify({'error': f"Step not found with id {step_id}"}), 404
    return jsonify(f'Trigger {step_id} deleted.')
