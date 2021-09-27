"""main Lexie app"""
import json

import click
from flask import Flask, redirect
from flask_socketio import SocketIO

from lexie.caching import flush_cache
from lexie.smarthome.models import db as sqla_db
from lexie.smarthome.models import prepare_db

socketio = SocketIO()

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
    socketio.init_app(app, cors_allowed_origins='*')
    prepare_db()
    # logger = logging.basicConfig(level=logging.DEBUG)
    # logging.getLogger().addHandler(logger)
    # load all device statuses to cache
    # if not testing:
    #     with app.app_context(): # pragma: nocover
    #         get_all_devices() # pragma: nocover
    @app.cli.command('create-db')
    def create_db_command(): # pragma: nocover
        """ Clear existing data and create new tables """
        sqla_db.create_all()
        click.echo('Database initialized')
    return app
