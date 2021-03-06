import logging

from lexie.app import create_app, socketio, event_listener_start
from lexie.smarthome.Routine import schedule_all_timers

app = create_app()
event_listener_start(app)
schedule_all_timers()

if __name__ == '__main__':
    socketio.run(app)
# else:
#     gunicorn_logger = logging.getLogger('gunicorn.error')
    # app.logger.handlers = gunicorn_logger.handlers
    # app.logger.setLevel(gunicorn_logger.level)
