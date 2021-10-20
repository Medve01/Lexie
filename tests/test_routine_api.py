import json

import pytest

from lexie.smarthome.lexiedevice import LexieDevice, LexieDeviceType
from lexie.smarthome import exceptions
from tests.fixtures.test_flask_app import app, api_client as client, client as noauth_client
from tests.fixtures.mock_lexieclasses import MockLexieDevice
from lexie.smarthome.routine import StepType, TriggerType, DeviceEvent
from lexie.smarthome.exceptions import NotFoundException

MOCK_CALLED = ''

class MockTrigger:
    def __init__(self, trigger_id) -> None:
        if trigger_id == 'VOID':
            raise NotFoundException
        self.id = trigger_id #pylint: disable=invalid-name
        self.type = TriggerType.DeviceEvent
        self.device_id = '1234'
        self.device = MockLexieDevice('1234')
        self.event = DeviceEvent.StateChanged
        self.next_step = None
        self.name = 'Test trigger'
        self.enabled = True
        self.trigger_dict = {
            'id': self.id, #pylint: disable=invalid-name
            'type': TriggerType.DeviceEvent,
            'device': '1234',
            'event': DeviceEvent.StateChanged,
            'next_step': None,
            'name': 'Test trigger',
            'enabled': True,
        }
    @staticmethod
    def get_all():
        return [MockTrigger('1234'), MockTrigger('4321')]
    
    def delete(self):
        global MOCK_CALLED
        MOCK_CALLED = 'MockTrigger.delete'

class MockStep:
    def __init__(self, step_id) -> None:
        if step_id == 'VOID':
            raise NotFoundException
        self.step_type = StepType.Delay
        self.id = step_id #pylint: disable=invalid-name
        self.next_step = None
        self.delay_duration = 1
        self.step_dict = {
            'id': step_id,
            'next_step': None,
            'delay_duration': 1,
            'step_type': StepType.Delay
        }

    def delete(self):
        global MOCK_CALLED
        MOCK_CALLED = 'MockStep.delete'

def test_step_get_noauth(noauth_client):
    result = noauth_client.get('/api/step/1234')
    assert result.status_code == 403

def test_trigger_get_noauth(noauth_client):
    result = noauth_client.get('/api/trigger/1234')
    assert result.status_code == 403

def test_step_delete(monkeypatch, app, client):
    monkeypatch.setattr('lexie.smarthome.routine.Step.__init__', MockStep.__init__)
    monkeypatch.setattr('lexie.smarthome.routine.Step.delete', MockStep.delete)
    result = client.delete('/api/step/1234')
    assert result.status_code == 200

def test_step_get(monkeypatch, app, client):
    monkeypatch.setattr('lexie.smarthome.routine.Step.__init__', MockStep.__init__)
    result = client.get('/api/step/1234')
    assert result.status_code == 200

def test_step_delete_nonexisting(monkeypatch, app, client):
    monkeypatch.setattr('lexie.smarthome.routine.Step.__init__', MockStep.__init__)
    monkeypatch.setattr('lexie.smarthome.routine.Step.delete', MockStep.delete)
    result = client.delete('/api/step/VOID')
    assert result.status_code == 404

def test_step_get_nonexisting(monkeypatch, app, client):
    monkeypatch.setattr('lexie.smarthome.routine.Step.__init__', MockStep.__init__)
    result = client.get('/api/step/VOID')
    assert result.status_code == 404

def test_trigger_delete(monkeypatch, app, client):
    monkeypatch.setattr('lexie.smarthome.routine.Trigger.__init__', MockTrigger.__init__)
    monkeypatch.setattr('lexie.smarthome.routine.Trigger.delete', MockTrigger.delete)
    result = client.delete('/api/trigger/1234')
    assert result.status_code == 200

def test_trigger_get(monkeypatch, app, client):
    monkeypatch.setattr('lexie.smarthome.routine.Trigger.__init__', MockTrigger.__init__)
    result = client.get('/api/trigger/1234')
    assert result.status_code == 200

def test_trigger_delete_nonexisting(monkeypatch, app, client):
    monkeypatch.setattr('lexie.smarthome.routine.Trigger.__init__', MockTrigger.__init__)
    monkeypatch.setattr('lexie.smarthome.routine.Trigger.delete', MockTrigger.delete)
    result = client.delete('/api/trigger/VOID')
    assert result.status_code == 404

def test_trigger_get_nonexisting(monkeypatch, app, client):
    monkeypatch.setattr('lexie.smarthome.routine.Trigger.__init__', MockTrigger.__init__)
    result = client.get('/api/trigger/VOID')
    assert result.status_code == 404

def test_trigger_get_all(monkeypatch, app, client):
    monkeypatch.setattr('lexie.smarthome.routine.Trigger.__init__', MockTrigger.__init__)
    monkeypatch.setattr('lexie.smarthome.routine.Trigger.get_all', MockTrigger.get_all)
    result = client.get('/api/trigger/')
    assert result.status_code == 200
    assert len(json.loads(result.data)) == 2
