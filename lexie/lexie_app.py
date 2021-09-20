"""main Lexie app"""
import json

from flask import Flask, redirect

from lexie.caching import flush_cache

from . import api, db, events, views

# import logging



# from lexie.smarthome.LexieDevice import get_all_devices

def create_app(testing:bool=False):#pylint: disable=unused-argument
    """default app"""
    flush_cache()
    app = Flask(__name__)
    app.config.from_file("config.json", load=json.load)
    @app.route('/')
    def index():
        return redirect('/ui')

    app.register_blueprint(api.api_bp)
    app.register_blueprint(views.ui_bp)
    app.register_blueprint(events.events_bp)
    db.init_app(app)
    # logger = logging.basicConfig(level=logging.DEBUG)
    # logging.getLogger().addHandler(logger)
    # load all device statuses to cache
    # if not testing:
    #     with app.app_context(): # pragma: nocover
    #         get_all_devices() # pragma: nocover
    return app
