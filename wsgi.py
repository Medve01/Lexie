import logging

from lexie.app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app)
else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
