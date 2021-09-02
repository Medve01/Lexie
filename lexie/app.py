"""main Lexie app"""
from flask import Flask

from . import api

# from .devices.device import LexieDevice


def create_app():
    """default app"""
    app = Flask(__name__)

    @app.route('/')
    def index():
        return 'Nothing to see here - yet.'

    app.register_blueprint(api.api_bp)
    return app
