"""main Lexie app"""
import json
import threading

import click
from flask import Flask, redirect
from flask_socketio import SocketIO

from lexie.caching import flush_cache
from lexie.smarthome import models
from lexie.smarthome.LexieDevice import LexieDevice
from lexie.smarthome.models import db as sqla_db
from lexie.smarthome.models import prepare_db

socketio = SocketIO()
POOL_TIME = 1 #seconds
EVENT_LISTENER_THREAD = threading.Thread() # pylint: disable=bad-thread-instantiation


def event_listener():
    """ fetches and handles events from database """
    print('Fetching events')
    event = models.db.session.query(models.Event).order_by(models.Event.id.desc()).first()
    while event:
        print(f'Event received from {event.device_id}: {event.event}') # pylint: disable=logging-fstring-interpolation
        device = LexieDevice(event.device_id)
        event_data = json.loads(event.event)
        if event_data['event_type'] == 'status':
            if event_data['event_data'] == 'on':
                device.set_status('ison', True)
            elif event_data['event_data'] == 'off':
                device.set_status('ison', False)
            socketio.emit('event', {'device_id': device.device_id, 'event': event_data})
        models.db.session.delete(event)
        models.db.session.commit()
        event = models.db.session.query(models.Event).order_by(models.Event.id.desc()).first()
    global EVENT_LISTENER_THREAD # pylint: disable=global-statement
    EVENT_LISTENER_THREAD = threading.Timer(POOL_TIME, event_listener, ())
    EVENT_LISTENER_THREAD.start()

def event_listener_start():
    """ starts event_listener thread on start """
    print('Starting event listener')
    global EVENT_LISTENER_THREAD # pylint: disable=global-statement
    EVENT_LISTENER_THREAD = threading.Timer(POOL_TIME, event_listener, ())
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
    # isort: on
    app.register_blueprint(device_api_bp)
    app.register_blueprint(room_api_bp)
    app.register_blueprint(ui_bp)
    app.register_blueprint(events_bp)
    sqla_db.app = app
    sqla_db.init_app(app)
    # socketio.init_app(app, cors_allowed_origins='*', async_mode='eventlet')
    socketio.init_app(app, cors_allowed_origins='*')
    prepare_db()
    event_listener_start()
    @app.cli.command('create-db')
    def create_db_command(): # pragma: nocover
        """ Clear existing data and create new tables """
        sqla_db.create_all()
        click.echo('Database initialized')
    return app
