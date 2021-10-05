import pytest

from tests.fixtures.test_flask_app import MOCK_CALLED, app, client
from tests.fixtures.mock_lexieclasses import MockLexieDevice, device_data
from lexie.smarthome.exceptions import InvalidEventException, NotFoundException
from lexie.smarthome import models
from lexie.smarthome.events import send_event
from lexie.app import event_listener


MOCK_CALL = {}

# def test_event_hook_invalid_event(client):
#     """tests default page"""
#     res = client.get('/events/1234/switched_on')
#     assert res.json == {"Error": "Invalid event"}

@pytest.mark.parametrize(
    ('event', 'status', 'results'),
    [
        # (
        #     'on',
        #     200,
        #     {
        #         'device_id': '1234',
        #         'status_name': 'ison',
        #         'status_value': True
        #     },
        # ),
        # (
        #     'off',
        #     200,
        #     {
        #         'device_id': '1234',
        #         'status_name': 'ison',
        #         'status_value': False
        #     },
        # ),
        # (
        #     'blarftegh',
        #     400,
        #     {}
        # )
        (
            'on',
            200,
            {
                'device_id': '1234',
                'event_type': 'status',
                'event_data': 'on'
            },
        ),
        (
            'off',
            200,
            {
                'device_id': '1234',
                'event_type': 'status',
                'event_data': 'off'
            },
        ),
        (
            'blarftegh',
            400,
            {}
        )    ]
)
def test_event_hook(monkeypatch, client, event, status, results):
    global MOCK_CALL
    MOCK_CALL = {}
    def mock_send_event(device_id, event, event_type):
        global MOCK_CALL
        MOCK_CALL = {
            'device_id': device_id,
            'event_data': event,
            'event_type': event_type
        }

    # def mock_get_status(self):
    #     if event == 'on':
    #         return {
    #             'online': True,
    #             'ison': True
    #         }
    #     if event == 'off':
    #         return {
    #             'online': True,
    #             'ison': False
    #         }
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.events.send_event', mock_send_event)
    # monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.set_status', mock_set_status)
    # monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.get_status', mock_get_status)
    res = client.get('/events/1234/' + event)
    assert res.status_code == status
    assert MOCK_CALL == results

def test_event_hook_nodevice(monkeypatch, client):
    def mocklexiedevice_init(self, device_id):
        raise NotFoundException
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', mocklexiedevice_init)

    res = client.get('events/6666/on')
    assert res.status_code == 404

MOCK_SIO_CALL = {}

@pytest.mark.parametrize('onoff, result',[
    (
        'on', {'channel': 'event', 'message':{'device_id': '1234', 'event': {'event_data': 'on', 'event_type': 'status'}}}
    ),
    (
        'off', {'channel': 'event', 'message':{'device_id': '1234', 'event': {'event_data': 'off', 'event_type': 'status'}}}
    )
])
def test_event_listener(app, monkeypatch, onoff, result):
    def mock_socketio_emit(channel, message):
        global MOCK_SIO_CALL
        MOCK_SIO_CALL = {
            'channel': channel,
            'message': message
        }
    def mock_set_status(self, value_name, value):
        global MOCK_CALL
        MOCK_CALL = {
            'device_id': self.device_id,
            'status_name': value_name,
            'status_value': value
        }
        return
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.app.socketio.emit', mock_socketio_emit)
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.set_status', mock_set_status)
    # put an event in DB
    global MOCK_SIO_CALL, MOCK_CALL
    MOCK_SIO_CALL = {}
    MOCK_CALL = {}
    with app.app_context():
        send_event('1234', onoff, 'status')
        event_listener(once=True)
    # call event_listener
    # verify if mock_socketio_emit and mock_set_status were properly called
    assert MOCK_SIO_CALL == result
