import json
from lexie.smarthome.models import Device

import pytest

from tests.fixtures.test_flask_app import MOCK_CALLED, app, routines_db
from tests.fixtures.mock_lexieclasses import MockLexieDevice
from lexie.smarthome.LexieDevice import LexieDevice
from lexie.smarthome.Routine import Trigger, TriggerType, Step, StepType, DeviceAction, InvalidParametersException, CannotDeleteException, NextStepAlreadyDefinedException, DeviceEvent
from lexie.smarthome.exceptions import NotFoundException
from lexie.app import check_and_fire_trigger

MOCK_CALLED=''

def test_trigger_CRD(monkeypatch, app, routines_db):
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', MockLexieDevice.__init__)
    with app.app_context():
        device = LexieDevice('1234')
        trigger = Trigger.new(name='Test trigger', trigger_type=TriggerType.DeviceEvent, device=device, event=DeviceEvent.TurnedOn)
    assert trigger.device_id == '1234'
    trigger_id = trigger.id
    with app.app_context():
        trigger.delete()
        with pytest.raises(NotFoundException):
            trigger = Trigger(trigger_id)

def test_trigger_notfound(app, routines_db):
    with app.app_context():
        with pytest.raises(NotFoundException):
            trigger = Trigger('666666')

def test_step_deviceaction_CRD(monkeypatch, app, routines_db):
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', MockLexieDevice.__init__)
    with app.app_context():
        device = LexieDevice('1234')
        step = Step.new(StepType.DeviceAction, device, DeviceAction.TurnOn)

    assert step.device.device_id == '1234' and step.step_type == StepType.DeviceAction and step.action == DeviceAction.TurnOn
    step_id = step.id
    with app.app_context():
        step.delete()
        with pytest.raises(NotFoundException):
            step = Step(step_id)

def test_step_delay_CRD(monkeypatch, app, routines_db):
    with app.app_context():
        device = LexieDevice('1234')
        step = Step.new(StepType.Delay, delay_duration=5)

    assert step.delay_duration == 5 and step.step_type == StepType.Delay
    step_id = step.id
    with app.app_context():
        step.delete()
        with pytest.raises(NotFoundException):
            step = Step(step_id)

def test_step_new_invalidparams(app, routines_db):
    with app.app_context():
        with pytest.raises(InvalidParametersException):
            step = Step.new(StepType.Delay, device_action=DeviceAction.TurnOff)

def test_step_notfound(app, routines_db):
    with app.app_context():
        with pytest.raises(NotFoundException):
            step = Step('666666')

def test_trigger_with_next(monkeypatch, app, routines_db):
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', MockLexieDevice.__init__)
    with app.app_context():
        device = LexieDevice('1234')
        trigger = Trigger.new(
            name='Test trigger',
            trigger_type=TriggerType.DeviceEvent,
            device= device,
            event= DeviceEvent.TurnedOff)
        step = Step.new(StepType.Delay, delay_duration=1)
        trigger.add_next(step)
        trigger_id = trigger.id
        trigger = Trigger(trigger_id)
        assert trigger.next_step == step.id
        with pytest.raises(CannotDeleteException):
            trigger.delete()
        step.delete()
        trigger = Trigger(trigger_id)
        assert trigger.next_step is None

def test_step_with_next(app, routines_db):
    with app.app_context():
        first_step = Step.new(step_type=StepType.Delay, delay_duration=1)
        second_step = Step.new(step_type=StepType.Delay, delay_duration=1)
        first_step.add_next(second_step)
        first_step_id = first_step.id
        step = Step(first_step_id)
        assert step.next_step.id == second_step.id
        with pytest.raises(CannotDeleteException):
            step.delete()
        second_step.delete()
        step = Step(first_step_id)
        assert step.next_step is None

def test_step_double_next(app, routines_db):
    with app.app_context():
        first_step = Step.new(step_type=StepType.Delay, delay_duration=1)
        second_step = Step.new(step_type=StepType.Delay, delay_duration=1)
        third_step = Step.new(step_type=StepType.Delay, delay_duration=1)
        first_step.add_next(second_step)
        with pytest.raises(NextStepAlreadyDefinedException):
            first_step.add_next(third_step)

def test_trigger_double_next(monkeypatch, app, routines_db):
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', MockLexieDevice.__init__)
    with app.app_context():
        first_step = Step.new(step_type=StepType.Delay, delay_duration=1)
        second_step = Step.new(step_type=StepType.Delay, delay_duration=1)
        trigger = Trigger.new(
            name='Test trigger',
            trigger_type=TriggerType.DeviceEvent,
            device=LexieDevice('1234'),
            event=DeviceEvent.StateChanged)
        trigger.add_next(first_step)
        with pytest.raises(NextStepAlreadyDefinedException):
            trigger.add_next(second_step)

def test_trigger_get_all(monkeypatch, app, routines_db):
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', MockLexieDevice.__init__)
    with app.app_context():
        triggers = []
        triggers.append(
            Trigger.new(
                name='test1',
                trigger_type=TriggerType.DeviceEvent,
                device=LexieDevice('1234'),
                event=DeviceEvent.TurnedOff
            )
        )
        triggers.append(
            Trigger.new(
                name='test2',
                trigger_type=TriggerType.DeviceEvent,
                device=LexieDevice('1234'),
                event=DeviceEvent.TurnedOff
            )
        )
        result = Trigger.get_all()
        for t in triggers:
            t.delete()
        assert len(result) == 2
        assert (
            result[0].id == triggers[0].id and
            result[0].device.device_id == triggers[0].device.device_id and
            result[0].type == triggers[0].type and
            result[0].event == triggers[0].event
        )
        assert (
            result[1].id == triggers[1].id and
            result[1].device.device_id == triggers[1].device.device_id and
            result[1].type == triggers[1].type and
            result[1].event == triggers[1].event
        )

def test_trigger_last_in_chain(monkeypatch, app, routines_db):
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', MockLexieDevice.__init__)
    with app.app_context():
        trigger = Trigger.new(
            name='test1',
            trigger_type=TriggerType.DeviceEvent,
            device=LexieDevice('1234'),
            event=DeviceEvent.TurnedOff
        )
        step1 = Step.new(
            step_type = StepType.Delay,
            delay_duration= 1
        )
        step2 = Step.new(
            step_type = StepType.Delay,
            delay_duration= 1
        )
        trigger.add_next(step1)
        step1.add_next(step2)
        last = trigger.last_in_chain()
        assert last.id == step2.id

def test_trigger_chain_to_list(monkeypatch, app, routines_db):
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', MockLexieDevice.__init__)
    with app.app_context():
        trigger = Trigger.new(
            name='test1',
            trigger_type=TriggerType.DeviceEvent,
            device=LexieDevice('1234'),
            event=DeviceEvent.TurnedOff
        )
        step1 = Step.new(
            step_type = StepType.Delay,
            delay_duration= 1
        )
        step2 = Step.new(
            step_type = StepType.Delay,
            delay_duration= 1
        )
        trigger.add_next(step1)
        step1.add_next(step2)
        result = trigger.chain_to_list()
        assert len(result)==2

def test_trigger_chain_to_list_no_steps(monkeypatch, app, routines_db):
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', MockLexieDevice.__init__)
    with app.app_context():
        trigger = Trigger.new(
            name='test1',
            trigger_type=TriggerType.DeviceEvent,
            device=LexieDevice('1234'),
            event=DeviceEvent.TurnedOff
        )
        assert trigger.chain_to_list() == []

def test_trigger_last_in_chain_no_steps(monkeypatch, app, routines_db):
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', MockLexieDevice.__init__)
    with app.app_context():
        trigger = Trigger.new(
            name='test1',
            trigger_type=TriggerType.DeviceEvent,
            device=LexieDevice('1234'),
            event=DeviceEvent.TurnedOff
        )
        assert trigger.last_in_chain() == trigger

def test_trigger_disable_enable(monkeypatch, app, routines_db):
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', MockLexieDevice.__init__)
    with app.app_context():
        trigger = Trigger.new(
            name='test1',
            trigger_type=TriggerType.DeviceEvent,
            device=LexieDevice('1234'),
            event=DeviceEvent.TurnedOff
        )
        assert trigger.enabled is True
        trigger.disable()
        assert trigger.enabled is False
        trigger = Trigger(trigger.id)
        assert trigger.enabled is False
        trigger.enable()
        assert trigger.enabled is True
        trigger = Trigger(trigger.id)
        assert trigger.enabled is True

def mock_device_turn(self, ison:bool):
    global MOCK_CALLED
    if ison:
        MOCK_CALLED = 'mock_device_turn_on'
        return {
            'online': True,
            'ison': True
        }
    MOCK_CALLED = 'mock_device_turn_off'
    return {
        'online': True,
        'ison': False
    }
def mock_device_toggle(self):
    global MOCK_CALLED
    MOCK_CALLED = 'mock_device_toggle'
    return {
        'online': True,
        'ison': False
    }

@pytest.mark.parametrize(('command', 'result'),
        (
            (DeviceAction.TurnOn,'mock_device_turn_on'),
            (DeviceAction.TurnOff, 'mock_device_turn_off'),
            (DeviceAction.Toggle, 'mock_device_toggle')
        )
)
def test_trigger_fire_deviceaction(monkeypatch, app, routines_db, command, result):
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.action_turn', mock_device_turn)
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.action_toggle', mock_device_toggle)
    with app.app_context():
        trigger = Trigger.new(name='Test trigger', trigger_type=TriggerType.DeviceEvent, device=LexieDevice('1234'), event=DeviceEvent.TurnedOn)
        step = Step.new(step_type=StepType.DeviceAction, device=LexieDevice('4321'), device_action=command)
        trigger.add_next(step)
        trigger.fire()
    assert MOCK_CALLED==result

def test_trigger_fire_delay(monkeypatch, app, routines_db):
    def mock_sleep(delay):
        global MOCK_CALLED
        MOCK_CALLED='mock_sleep'
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.action_turn', mock_device_turn)
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.action_toggle', mock_device_toggle)
    monkeypatch.setattr('time.sleep', mock_sleep)
    with app.app_context():
        trigger = Trigger.new(name='Test trigger', trigger_type=TriggerType.DeviceEvent, device=LexieDevice('1234'), event=DeviceEvent.TurnedOn)
        step = Step.new(step_type=StepType.Delay, delay_duration=1)
        trigger.add_next(step)
        step.add_next(Step.new(step_type=StepType.Delay, delay_duration=1))
        trigger.fire()
    assert MOCK_CALLED=='mock_sleep'

@pytest.mark.parametrize(
    ('event'),
    (
        (DeviceEvent.TurnedOn),(DeviceEvent.TurnedOff), (DeviceEvent.StateChanged)
    )
)
def test_check_and_fire_trigger(monkeypatch, app, routines_db, event):
    def mock_trigger_fire(self):
        global MOCK_CALLED
        MOCK_CALLED='mock_trigger_fire'
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', MockLexieDevice.__init__)
    monkeypatch.setattr('lexie.smarthome.Routine.Trigger.fire', mock_trigger_fire)
    with app.app_context():
        trigger = Trigger.new(name='Test trigger', trigger_type=TriggerType.DeviceEvent, device=LexieDevice('1234'), event=event)
        global MOCK_CALLED
        MOCK_CALLED=''
        check_and_fire_trigger(event_type=event, device_id='1234')
    assert MOCK_CALLED=='mock_trigger_fire'