
import logging
import os

from flask import Blueprint, redirect, render_template, request
from jinja2 import TemplateNotFound

from lexie.apikey import generate_apikey, have_apikey
from lexie.smarthome import models
from lexie.smarthome.lexiedevice import (LexieDevice, LexieDeviceType,
                                         get_all_devices,
                                         get_all_devices_with_rooms)
from lexie.smarthome.room import Room
from lexie.smarthome.routine import (DeviceAction, DeviceEvent, Step, StepType,
                                     Trigger, TriggerTimer, TriggerType)

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

@ui_bp.route('/apikey/generate', methods=['GET'])
def apikey_generate():
    """ create a new api key, store it in TinyDB. Override if we have an existing one """
    apikey = generate_apikey()
    return render_template('apikey_generate.html', apikey=apikey)


@ui_bp.route('/apikey', methods=['GET'])
def apikey_get():
    """ If we have an API key stored, then show this fact UI. """
    return render_template('apikey.html', have_apikey = have_apikey())

@ui_bp.route('/move_device', methods=['POST'])
def move_device():
    """ post target for dashboard move device modal form """
    device = LexieDevice(request.form.get('device_id'))
    device.move(Room(request.form.get('room_id')))
    return redirect('/ui')

@ui_bp.route('/add-trigger', methods=['POST'])
def add_trigger():
    """ post target for New routine page """
    form_trigger_type = request.form.get('trigger_type')
    if form_trigger_type == 'DeviceEvent':
        trigger = Trigger.new(
            trigger_type = TriggerType.DeviceEvent, # pylint: disable=protected-access
            name=request.form.get('routine_name'),
            device = LexieDevice(request.form.get('device')),
            event = DeviceEvent._as_dict[request.form.get('event')]) # pylint: disable=protected-access
    elif form_trigger_type == 'Timer':
        days_of_week = []
        if request.form.get('monday') == '1':
            days_of_week.append(1)
        if request.form.get('tuesday') == '1':
            days_of_week.append(2)
        if request.form.get('wednesday') == '1':
            days_of_week.append(3)
        if request.form.get('thursday') == '1':
            days_of_week.append(4)
        if request.form.get('friday') == '1':
            days_of_week.append(5)
        if request.form.get('saturday') == '1':
            days_of_week.append(6)
        if request.form.get('sunday') == '1':
            days_of_week.append(7)

        hour = request.form.get('selectTime').split(':')[0]
        minute = request.form.get('selectTime').split(':')[1]
        timer = TriggerTimer.new()
        if len(days_of_week) == 0:
            timer.add_schedule(hour=hour, minute=minute)
        else:
            for day_of_week in days_of_week:
                timer.add_schedule(day_of_week=day_of_week, hour=hour, minute=minute)
        trigger = Trigger.new(
            name=request.form.get('routine_name'),
            trigger_type=TriggerType.Timer,
            timer=timer
        )

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

@ui_bp.route('/remove-action/<trigger_id>/<step_id>')
def remove_action(trigger_id, step_id):
    """ removes an action from a routine chain """
    step = Step(step_id)
    step.delete()
    return redirect('/ui/edit-routine/' + trigger_id)

@ui_bp.route('/remove-routine/<trigger_id>')
def remove_routine(trigger_id):
    """ Deletes a routine """
    trigger = Trigger(trigger_id)
    trigger.delete()
    return redirect('/ui/routines')

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
        if segment == 'login':
            return render_template( segment + '.html')
        if segment == 'eventlog':
            # events = models.db.Query(models.EventLog).order_by(models.EventLog.timestamp.desc()).limit(100)
            events = models.EventLog.query.order_by(models.EventLog.timestamp.desc()).limit(100)
            return render_template( segment + '.html', events=events)
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
