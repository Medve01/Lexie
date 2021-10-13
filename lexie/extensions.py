import logging

from flask_apscheduler import APScheduler
from flask_socketio import SocketIO

socketio = SocketIO()
scheduler = APScheduler()
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
