from typing import Any
from urllib.parse import urlparse

import pytest

from lexie.smarthome.lexiedevice import LexieDevice, LexieDeviceType
from lexie.views import get_drivers
from tests.fixtures.test_flask_app import app, client, routines_db
from tests.fixtures.mock_lexieclasses import MockLexieDevice, MockRoom
from lexie.smarthome.routine import DeviceAction, DeviceEvent, Step, StepType, Trigger, TriggerType


def mock_os_listdir(directory):
    if directory=='./lexie/drivers':
        return [
            '__init__.py',
            'shelly',
            'xiaomi'
        ]
    if directory=='./lexie/drivers/shelly':
        return [
                'shelly1.py',
                'shelly_motion.py'
            ]
    if directory=='./lexie/drivers/xiaomi':
        return ['dreamemoppro.py']

def test_default_page(client):
    """tests default page"""
    res = client.get('/')
    assert res.status_code == 302
    parsed_response_url = urlparse(res.location)
    assert parsed_response_url.path == '/ui'

def test_ui_dashboard(client):
    """tests default page"""
    res = client.get('/ui/')
    assert res.status_code == 200

def test_ui_device_list(client):
    """tests default page"""
    res = client.get('/ui/device-list')
    assert res.status_code == 200

def test_ui_404(client):
    """ tests page not found """
    res = client.get('/ui/szlartibartfaszt')
    assert res.status_code == 404

def test_ui_views_get_drivers(monkeypatch):

    monkeypatch.setattr('os.listdir', mock_os_listdir)
    result = get_drivers()
    assert result == [
        'shelly - shelly1',
        'shelly - shelly_motion',
        'xiaomi - dreamemoppro'
    ]

def test_add_device_get(monkeypatch,client):
    monkeypatch.setattr('os.listdir', mock_os_listdir)
    result=client.get('/ui/add-device')
    assert result.status_code == 200

def test_add_device_post(monkeypatch, client):
    def mock_lexiedevice_new(**kwargs):
        global passed_arguments_to_mock
        passed_arguments_to_mock = kwargs
        return "666666"
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.new', mock_lexiedevice_new)
    result = client.post('/ui/add-device', data={
        #         device_name=device_data['device_name'],
        # device_type=LexieDeviceType(device_data['device_type']),
        # device_manufacturer=device_data['device_driver'].split('-')[0].strip(),
        # device_product=device_data['device_driver'].split('-')[1].strip(),
        # device_attributes={'ip_address': device_data['device_ip']}
        'device_name': 'Test device',
        'device_type': 1,
        'device_driver': 'shelly - shelly1',
        'device_ip': '127.0.0.1'
    })
    assert result.status_code == 302
    assert (passed_arguments_to_mock['device_name'] == 'Test device' and
        isinstance(passed_arguments_to_mock['device_type'], LexieDeviceType) and
        passed_arguments_to_mock['device_manufacturer'] == 'shelly' and
        passed_arguments_to_mock['device_product'] == 'shelly1' and
        passed_arguments_to_mock['device_attributes'] == {'ip_address': '127.0.0.1'}
    )

def test_move_device(monkeypatch, client):
    def mock_move_device(self, room):
        global passed_arguments_to_mock
        passed_arguments_to_mock = room
        return
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.move', mock_move_device)
    monkeypatch.setattr('lexie.smarthome.room.Room.__init__', MockRoom.__init__)
    result = client.post('/ui/move_device', data={
        'device_id': '1234',
        'room_id': '1234',
    })
    global passed_arguments_to_mock
    assert result.status_code == 302
    assert passed_arguments_to_mock.id == '1234'

def test_routine_list_get(monkeypatch, client, routines_db):
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.room.Room.__init__', MockRoom.__init__)
    result = client.get('/ui/routines')
    assert result.status_code == 200

def test_add_routine_get(monkeypatch, client, routines_db):
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.room.Room.__init__', MockRoom.__init__)
    result = client.get('/ui/add-routine')
    assert result.status_code == 200

def test_add_routine_post_deviceevent(monkeypatch, client, app, routines_db):
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.room.Room.__init__', MockRoom.__init__)
    result = client.post('/ui/add-trigger', data={
        'trigger_type': 'DeviceEvent',
        'routine_name': 'Test routine',
        'device': '1234',
        'event': 'TurnedOn'
    })
    assert result.status_code == 302
    with app.app_context():
        trigger_id = result.location.split('/')[-1]
        trigger = Trigger(trigger_id)

def test_add_routine_post_timer_alldays(monkeypatch, client, app, routines_db):
    result = client.post('/ui/add-trigger', data={
        'trigger_type': 'Timer',
        'routine_name': 'Test routine',
        'selectTime': '13:00'
    })
    assert result.status_code == 302
    with app.app_context():
        trigger_id = result.location.split('/')[-1]
        trigger = Trigger(trigger_id)

@pytest.mark.parametrize("day", (
    [
        ('monday'),
        ('tuesday'),
        ('wednesday'),
        ('thursday'),
        ('friday'),
        ('saturday'),
        ('sunday'),
    ]
))
def test_add_routine_post_timer_days(client, app, day):
    result = client.post('/ui/add-trigger', data={
        'trigger_type': 'Timer',
        'routine_name': 'Test routine',
        day: '1',
        'selectTime': '13:00'
    })
    assert result.status_code == 302
    with app.app_context():
        trigger_id = result.location.split('/')[-1]
        trigger = Trigger(trigger_id)
        assert len(trigger.timer.schedules) == 1

def test_add_routine_post_timer_multiple_days(client, app):
    result = client.post('/ui/add-trigger', data={
        'trigger_type': 'Timer',
        'routine_name': 'Test routine',
        'monday': '1',
        'tuesday': '1',
        'wednesday': '1',
        'thursday': '1',
        'friday': '1',
        'sunday': '1',
        'selectTime': '13:00'
    })
    assert result.status_code == 302
    with app.app_context():
        trigger_id = result.location.split('/')[-1]
        trigger = Trigger(trigger_id)
        assert len(trigger.timer.schedules) == 6

def test_edit_routine_get(monkeypatch, client, app, routines_db):
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.room.Room.__init__', MockRoom.__init__)
    with app.app_context():
        trigger = Trigger.new(
            trigger_type=TriggerType.DeviceEvent,
            device=LexieDevice('1234'),
            event=DeviceEvent.TurnedOn,
            name='Test trigger'
        )
        result = client.get('/ui/edit-routine/' + trigger.id)
    assert result.status_code == 200

def test_edit_routine_post_step_deviceaction(monkeypatch, client, app, routines_db):
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.room.Room.__init__', MockRoom.__init__)
    with app.app_context():
        trigger = Trigger.new(
            trigger_type=TriggerType.DeviceEvent,
            device=LexieDevice('1234'),
            event=DeviceEvent.TurnedOn,
            name='Test trigger'
        )
        result = client.post('/ui/edit-routine/' + trigger.id, data={
            'step_type': 'DeviceAction',
            'device': LexieDevice('1234'),
            'action': 'TurnOn',
        })
        trigger = Trigger(trigger_id=trigger.id)
        assert result.status_code == 302
        assert urlparse(result.location).path == '/ui/edit-routine/' + trigger.id
        next_step = trigger.next_step
        assert next_step is not None

def test_edit_routine_post_step_delay(monkeypatch, client, app, routines_db):
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.room.Room.__init__', MockRoom.__init__)
    with app.app_context():
        trigger = Trigger.new(
            trigger_type=TriggerType.DeviceEvent,
            device=LexieDevice('1234'),
            event=DeviceEvent.TurnedOn,
            name='Test trigger'
        )
        result = client.post('/ui/edit-routine/' + trigger.id, data={
            'step_type': 'Delay',
            'delay_duration': '1',
        })
        trigger = Trigger(trigger_id=trigger.id)
        assert result.status_code == 302
        assert urlparse(result.location).path == '/ui/edit-routine/' + trigger.id
        next_step = trigger.next_step
        assert next_step is not None

def test_edit_routine_add_two_steps(monkeypatch, client, app, routines_db):
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.room.Room.__init__', MockRoom.__init__)
    with app.app_context():
        trigger = Trigger.new(
            trigger_type=TriggerType.DeviceEvent,
            device=LexieDevice('1234'),
            event=DeviceEvent.TurnedOn,
            name='Test trigger'
        )
        result = client.post('/ui/edit-routine/' + trigger.id, data={
            'step_type': 'Delay',
            'delay_duration': '1',
        })
        result = client.post('/ui/edit-routine/' + trigger.id, data={
            'step_type': 'Delay',
            'delay_duration': '1',
        })
        trigger = Trigger(trigger_id=trigger.id)
        assert result.status_code == 302
        assert urlparse(result.location).path == '/ui/edit-routine/' + trigger.id
        first_step = Step(trigger.next_step)
        second_step = first_step.next_step
        assert second_step is not None
        assert isinstance(second_step, Step)

def test_remove_action(monkeypatch, client, app, routines_db):
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.room.Room.__init__', MockRoom.__init__)
    with app.app_context():
        trigger = Trigger.new(
            name='Test routine',
            trigger_type=TriggerType.DeviceEvent,
            device=LexieDevice('1234'),
            event=DeviceEvent.StateChanged
        )
        step = Step.new(
            step_type=StepType.Delay,
            delay_duration=1
        )
        trigger.add_next(step)
    result = client.get('/ui/remove-action/' + trigger.id + '/' + step.id)
    assert result.status_code == 302

def test_remove_routine(monkeypatch, client, app, routines_db):
    monkeypatch.setattr('lexie.smarthome.lexiedevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.room.Room.__init__', MockRoom.__init__)
    with app.app_context():
        trigger = Trigger.new(
            name='Test routine',
            trigger_type=TriggerType.DeviceEvent,
            device=LexieDevice('1234'),
            event=DeviceEvent.StateChanged
        )
    result = client.get('/ui/remove-routine/' + trigger.id)
    assert result.status_code == 302
