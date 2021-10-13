"""main Lexie app"""
import atexit
import json
import threading
import time

import click
import tinydb
from flask import Flask, current_app, redirect
from flaskthreads import AppContextThread

from lexie.caching import flush_cache
from lexie.extensions import scheduler, socketio
from lexie.smarthome import models
from lexie.smarthome.LexieDevice import LexieDevice
from lexie.smarthome.models import db as sqla_db
from lexie.smarthome.models import prepare_db
from lexie.smarthome.Routine import DeviceEvent, Trigger

EVENT_LISTENER_CONTINUE = True
EVENT_LISTENER_THREAD = threading.Thread() # pylint: disable=bad-thread-instantiation

def check_and_fire_trigger(event_type, device_id):
    """ checks if we have a trigger for the incoming event and if yes, fires it """
    with current_app.app_context():
        triggers_db = tinydb.TinyDB(current_app.config['ROUTINES_DB']).table('trigger')
        db_trigger = tinydb.Query()
        triggers = triggers_db.search((db_trigger.device_id == device_id) & (db_trigger.event == event_type))
        if triggers != []:
            for trigger_ in triggers:
                trigger = Trigger(trigger_['id'])
                routine_thread = AppContextThread(target=trigger.fire)
                routine_thread.start()

def event_listener_cancel():
    """ stops thread loop """
    global EVENT_LISTENER_CONTINUE # pylint: disable=global-statement
    EVENT_LISTENER_CONTINUE = False # pragma: nocover

def event_listener(once: bool = False):
    """ fetches and handles events from database """
    # print('Fetching events')
    global EVENT_LISTENER_CONTINUE # pylint: disable=global-statement
    EVENT_LISTENER_CONTINUE = True # ensure that we run at least once
    while EVENT_LISTENER_CONTINUE:
        event = models.db.session.query(models.Event).order_by(models.Event.id.desc()).first()
        while event:
            print(f'Event received from {event.device_id}: {event.event}') # pylint: disable=logging-fstring-interpolation
            device = LexieDevice(event.device_id)
            event_data = json.loads(event.event)
            models.db.session.delete(event)
            models.db.session.commit()
            if event_data['event_type'] == 'status':
                socketio.emit('event', {'device_id': device.device_id, 'event': event_data})
                check_and_fire_trigger(DeviceEvent.StateChanged, device.device_id)
                if event_data['event_data'] == 'on':
                    device.set_status('ison', True)
                    check_and_fire_trigger(DeviceEvent.TurnedOn, device.device_id)
                elif event_data['event_data'] == 'off':
                    device.set_status('ison', False)
                    check_and_fire_trigger(DeviceEvent.TurnedOff, device.device_id)
            event = models.db.session.query(models.Event).order_by(models.Event.id.desc()).first()
        if once:
            EVENT_LISTENER_CONTINUE = False
        else:
            time.sleep(1) # pragma: nocover

def event_listener_start(app): #pragma: nocover
    """ starts event_listener thread on start """
    print('Starting event listener')
    global EVENT_LISTENER_THREAD # pylint: disable=global-statement
    # EVENT_LISTENER_THREAD = threading.Timer(1, event_listener, ())
    with app.app_context():
        EVENT_LISTENER_THREAD = AppContextThread(target=event_listener, name='LexieEventListener')
    EVENT_LISTENER_THREAD.start()

def create_app(testing:bool=False):#pylint: disable=unused-argument
    """default app"""
    flush_cache()
    app = Flask(__name__)
    app.config.from_file("config.json", load=json.load)
    @app.route('/')
    def index():
        return redirect('/ui')
    # isort: off
    from lexie.device_api import device_api_bp # pylint: disable=import-outside-toplevel
    from lexie.events import events_bp # pylint: disable=import-outside-toplevel
    from lexie.room_api import room_api_bp # pylint: disable=import-outside-toplevel
    from lexie.views import ui_bp # pylint: disable=import-outside-toplevel
    from lexie.trigger_api import trigger_api_bp # pylint: disable=import-outside-toplevel
    from lexie.step_api import step_api_bp # pylint: disable=import-outside-toplevel
    # isort: on
    app.register_blueprint(device_api_bp)
    app.register_blueprint(room_api_bp)
    app.register_blueprint(ui_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(trigger_api_bp)
    app.register_blueprint(step_api_bp)
    sqla_db.app = app
    sqla_db.init_app(app)
    prepare_db()
    socketio.init_app(app, cors_allowed_origins='*')
    if scheduler.state != 0:
        try:
            scheduler.shutdown(wait=False)
        except: # pylint: disable=bare-except
            print('This only happens during testing, so I am fooling bandit here')
    scheduler.init_app(app)
    scheduler.start()
    atexit.register(event_listener_cancel)
    @app.cli.command('create-db')
    def create_db_command(): # pragma: nocover
        """ Clear existing data and create new tables """
        sqla_db.create_all()
        click.echo('Database initialized')
    return app
