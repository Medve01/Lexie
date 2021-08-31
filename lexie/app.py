"""main Lexie app"""
from flask import Flask


def create_app():
    """default app"""
    app = Flask(__name__)

    @app.route('/')
    def index():
        return 'Hello World!'
    return app
