import json
from lexie.smarthome.models import Device

import pytest

from tests.fixtures.test_flask_app import app
from tests.fixtures.mock_lexieclasses import MockLexieDevice
from lexie.smarthome.LexieDevice import LexieDevice
from lexie.smarthome.Routine import Trigger, TriggerType, Step, StepType, DeviceAction, InvalidParametersException, CannotDeleteException, NextStepAlreadyDefinedException, DeviceEvent
from lexie.smarthome.exceptions import NotFoundException

def test_trigger_CRD(monkeypatch, app):
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', MockLexieDevice.__init__)
    with app.app_context():
        device = LexieDevice('1234')
        trigger = Trigger.new(TriggerType.DeviceEvent, device, DeviceAction.TurnOff)
    assert trigger.device_id == '1234'
    trigger_id = trigger.id
    with app.app_context():
        trigger.delete()
        with pytest.raises(NotFoundException):
            trigger = Trigger(trigger_id)

def test_trigger_notfound(app):
    with app.app_context():
        with pytest.raises(NotFoundException):
            trigger = Trigger('666666')

def test_step_deviceaction_CRD(monkeypatch, app):
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

def test_step_delay_CRD(monkeypatch, app):
    with app.app_context():
        device = LexieDevice('1234')
        step = Step.new(StepType.Delay, delay_duration=5)

    assert step.delay_duration == 5 and step.step_type == StepType.Delay
    step_id = step.id
    with app.app_context():
        step.delete()
        with pytest.raises(NotFoundException):
            step = Step(step_id)

def test_step_new_invalidparams(app):
    with app.app_context():
        with pytest.raises(InvalidParametersException):
            step = Step.new(StepType.Delay, device_action=DeviceAction.TurnOff)

def test_step_notfound(app):
    with app.app_context():
        with pytest.raises(NotFoundException):
            step = Step('666666')

def test_trigger_with_next(monkeypatch, app):
    monkeypatch.setattr('lexie.smarthome.LexieDevice.LexieDevice.__init__', MockLexieDevice.__init__)
    with app.app_context():
        device = LexieDevice('1234')
        trigger = Trigger.new(TriggerType.DeviceEvent, device, DeviceAction.TurnOff)
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
        trigger.delete()

def test_step_with_next(app):
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
        step.delete()
        second_step.delete()

def test_step_double_next(app):
    with app.app_context():
        first_step = Step.new(step_type=StepType.Delay, delay_duration=1)
        second_step = Step.new(step_type=StepType.Delay, delay_duration=1)
        third_step = Step.new(step_type=StepType.Delay, delay_duration=1)
        first_step.add_next(second_step)
        with pytest.raises(NextStepAlreadyDefinedException):
            first_step.add_next(third_step)
        third_step.delete()
        second_step.delete()
        first_step = Step(first_step.id)
        first_step.delete()

def test_trigger_double_next(app):
    with app.app_context():
        first_step = Step.new(step_type=StepType.Delay, delay_duration=1)
        second_step = Step.new(step_type=StepType.Delay, delay_duration=1)
        trigger = Trigger.new(trigger_type=TriggerType.DeviceEvent, device=LexieDevice('1234'), event=DeviceEvent.StateChanged)
        trigger.add_next(first_step)
        with pytest.raises(NextStepAlreadyDefinedException):
            trigger.add_next(second_step)
        first_step.delete()
        second_step.delete()
        trigger = Trigger(trigger.id)
        trigger.delete()
