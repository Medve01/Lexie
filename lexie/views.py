
# Flask modules
import logging
import os

from flask import Blueprint, redirect, render_template, request
from jinja2 import TemplateNotFound

from lexie.smarthome.LexieDevice import (LexieDevice, LexieDeviceType,
                                         get_all_devices,
                                         get_all_devices_with_rooms)
from lexie.smarthome.Room import Room
from lexie.smarthome.Routine import (DeviceAction, DeviceEvent, Step, StepType,
                                     Trigger, TriggerType)

# Register blueprint
ui_bp = Blueprint('ui', __name__, url_prefix='/ui')

# Helper - Extract current page name from request
def get_segment( path ):
    """ gets the word between http://127.0.0.1/ui/ and .html """
    try:
        segment = path.split('/')[-1]
        if segment == '':
            segment = 'dashboard' #pragma: nocover
        return segment
    except: # pylint: disable=bare-except # pragma nocover
        return None # pragma nocover

def get_drivers():
    """ Fetches the available drivers in the drivers folder"""
    drivers=[]
    elements=os.listdir('./lexie/drivers')
    # if elements is None:
    #     elements = os.listdir('./drivers')
    for item in elements:
        if item[0]!="_":
            modules = os.listdir('./lexie/drivers/' + item)
            for module in modules:
                if module[0] != "_":
                    drivers.append(item + " - " + module[:-3])
    return drivers

def get_attributes(cls):
    """ enumarates members of a given class, exluding private ones """
    return [i for i in cls.__dict__.keys() if not i.startswith('_')] # pylint: disable=consider-iterating-dictionary
@ui_bp.route('/move_device', methods=['POST'])
def move_device():
    """ post target for dashboard move device modal form """
    device = LexieDevice(request.form.get('device_id'))
    device.move(Room(request.form.get('room_id')))
    return redirect('/ui')

@ui_bp.route('/add-trigger', methods=['POST'])
def add_trigger():
    """ post target for New routine page """
    trigger = Trigger.new(
        trigger_type = TriggerType._as_dict[request.form.get('trigger_type')], # pylint: disable=protected-access
        name=request.form.get('routine_name'),
        device = LexieDevice(request.form.get('device')),
        event = DeviceEvent._as_dict[request.form.get('event')]) # pylint: disable=protected-access
    return redirect('/ui/edit-routine/' + trigger.id)

@ui_bp.route('edit-routine/<trigger_id>', methods=['GET'])
def add_step(trigger_id):
    """ Renders the "add step" page """
    trigger = Trigger(trigger_id)
    step_types = get_attributes(StepType)
    devices = get_all_devices_with_rooms()
    actions = get_attributes(DeviceAction)
    steps = trigger.chain_to_list()

    return render_template(
        'edit-routine.html',
        segment = 'edit-routine',
        trigger=trigger,
        step_types=step_types,
        devices=devices,
        actions=actions,
        steps = steps)

@ui_bp.route('edit-routine/<trigger_id>', methods=['POST'])
def save_step(trigger_id):
    """ post target for /ui/edit-routine """
    trigger = Trigger(trigger_id)
    step_type = StepType._as_dict[request.form.get('step_type')] # pylint: disable=protected-access
    if step_type == StepType.DeviceAction:
        step_to_add = Step.new(
            step_type=StepType.DeviceAction,
            device=LexieDevice(request.form.get('device')),
            device_action=DeviceAction._as_dict[request.form.get('action')] # pylint: disable=protected-access
        )
    elif step_type == StepType.Delay:
        step_to_add = Step.new(
            step_type=StepType.Delay,
            delay_duration=int(request.form.get('delay_duration'))
        )
    if trigger.next_step is None:
        trigger.add_next(step_to_add)
    else:
        last_in_chain = trigger.last_in_chain()
        last_in_chain.add_next(step_to_add)
    return redirect('/ui/edit-routine/' + trigger_id)

# App main route + generic routing
@ui_bp.route('/', defaults={'path': 'dashboard'})
@ui_bp.route('/<path>')
def index(path): # pylint: disable=too-many-return-statements
    """ renders default ui page """
    # I should really refactor this...
    try:

        # Detect the current page
        segment = get_segment( path )
        logging.info(segment)
        if segment in ('add-routine'):
            trigger_types = get_attributes(TriggerType)
            device_events = get_attributes(DeviceEvent)
            devices = get_all_devices_with_rooms()
            return render_template(
                segment + '.html',
                segment=segment,
                triggertypes = trigger_types,
                devices = devices,
                device_events = device_events
            )
        if segment in ('routines'):
            triggers = Trigger.get_all()
            return render_template( segment + '.html', segment=segment, triggers = triggers )
        if segment in ('device-list'):
            devices = get_all_devices()
            return render_template( segment + '.html', segment=segment, devices=devices )
        if segment in ('dashboard', 'index'):
            rooms = Room.get_all_rooms()
            return render_template( segment + '.html', segment=segment, rooms=rooms )
        if segment == "add-device":
            # drivers=get_drivers()
            return render_template( segment + '.html', drivers=get_drivers(), segment=segment)
        return render_template( segment + '.html', segment=segment)

        # Serve the file (if exists) from app/templates/FILE.html

    except TemplateNotFound:
        return render_template('page-404.html', segment=segment), 404

@ui_bp.route('/add-device', methods=["POST"])
def add_device():
    """ creates a new LexieDevice based on form data """
    device_data = request.form
    LexieDevice.new(
        device_name=device_data['device_name'],
        device_type=LexieDeviceType(device_data['device_type']),
        device_manufacturer=device_data['device_driver'].split('-')[0].strip(),
        device_product=device_data['device_driver'].split('-')[1].strip(),
        device_attributes={'ip_address': device_data['device_ip']}
    )
    return redirect( '/ui/device-list')
