import logging

from flask_apscheduler import APScheduler
from flask_login import LoginManager
from flask_socketio import SocketIO

socketio = SocketIO()
scheduler = APScheduler()
login_manager = LoginManager()
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
