"""main Lexie app"""
import json

from flask import Flask

from . import api, db


def create_app():
    """default app"""
    app = Flask(__name__)
    app.config.from_file("config.json", load=json.load)
    @app.route('/')
    def index():
        return 'Nothing to see here - yet.'

    app.register_blueprint(api.api_bp)
    db.init_app(app)
    return app
