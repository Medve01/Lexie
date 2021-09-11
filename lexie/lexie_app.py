"""main Lexie app"""
import json
import logging

from flask import Flask

from lexie.devices.LexieDevice import get_all_devices

from . import api, db, views


def create_app(testing:bool=False):
    """default app"""
    app = Flask(__name__)
    app.config.from_file("config.json", load=json.load)
    @app.route('/')
    def index():
        return 'Nothing to see here - yet.'

    app.register_blueprint(api.api_bp)
    app.register_blueprint(views.ui_bp)
    db.init_app(app)
    logging.basicConfig(level=logging.DEBUG)
    # load all device statuses to cache
    if not testing:
        with app.app_context(): # pragma: nocover
            get_all_devices() # pragma: nocover
    return app
