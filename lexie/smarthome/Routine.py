import time

import apscheduler
import tinydb  # pylint: disable=import-error
from flask import current_app
from shortuuid import uuid

from lexie.extensions import scheduler
from lexie.smarthome.exceptions import NotFoundException
from lexie.smarthome.LexieDevice import LexieDevice


class InvalidParametersException(Exception):
    """ to be raised if a Trigger.new() or Step.new() is called with an invalid parameter set """

class CannotDeleteException(Exception):
    """ to be raised if a Trigger.delete() or Step.delete() is called and the object has a next_step """

class NextStepAlreadyDefinedException(Exception):
    """ to be raised when attempting to call add_next() on a trigger or step that already has a next_step defined. """

def schedule_all_timers():
    """ parses through all triggers and adds a job for Timed ones.
        to be ran on app start """
    with scheduler.app.app_context():
        triggers = Trigger.get_all()
        for trigger in triggers:
            if trigger.type == TriggerType.Timer:
                for schedule in trigger.timer.schedules:
                    if schedule['day_of_week'] == 7:
                        schedule['day_of_week'] = 0
                    scheduler.add_job(
                        id='trigger_' + trigger.id + str(schedule['day_of_week']),
                        func=fire_trigger,
                        args=[trigger.id],
                        trigger='cron',
                        day_of_week=schedule['day_of_week'],
                        hour=schedule['hour'],
                        minute=schedule['minute']
                    )

def fire_trigger(trigger_id: str):
    """ to be used with APscheduler. Instanciates the Trigger(trigger_id) and fires it. """
    with scheduler.app.app_context():
        trigger = Trigger(trigger_id)
        trigger.fire()

def push_to_db(table, value):
    """ stores dict in TinyDB. key is dict['id'] """
    routines_db = tinydb.TinyDB(current_app.config['ROUTINES_DB'])
    db_table = routines_db.table(table)
    db_table.insert(value)

def fetch_from_db(table, key):
    """ fetches a dict from TinyDB. key is dict['id'] """
    routines_db = tinydb.TinyDB(current_app.config['ROUTINES_DB'])
    db_table = routines_db.table(table)
    value = db_table.search(tinydb.Query().id == key)
    if value == []:
        raise NotFoundException
    return value[0]

def delete_from_db(table, key):
    """ removes a dict from TinyDB. key is dict['id'] """
    routines_db = tinydb.TinyDB(current_app.config['ROUTINES_DB'])
    db_table = routines_db.table(table)
    db_table.remove(tinydb.Query().id == key)

def update_in_db(table, value):
    """ updates a record in TinyDB. value['id'] must exists, since we use that as key
        instead of wasting code on the update() of TinyDB, we'll just remove the old one and add a new one."""
    routines_db = tinydb.TinyDB(current_app.config['ROUTINES_DB'])
    db_table = routines_db.table(table)
    db_table.remove(tinydb.Query().id == value['id'])
    db_table.insert(value)

def search_in_db(table, key, value):
    """ searches the database for an attribute value
        returns only the first match"""
    routines_db = tinydb.TinyDB(current_app.config['ROUTINES_DB'])
    db_table = routines_db.table(table)
    result = db_table.search(tinydb.where(key) == value)
    if result == []:
        return None
    return result[0]

def fetch_all_from_db(table):
    """ fetches all records of a specific type """
    routines_db = tinydb.TinyDB(current_app.config['ROUTINES_DB'])
    db_table = routines_db.table(table)
    return db_table.all()

class DeviceEvent: # pylint: disable=too-few-public-methods
    """ supported Device Events in Triggers """
    TurnedOn = 'turned_on'
    TurnedOff = 'turned_off'
    StateChanged = 'state_changed'
    _as_dict = {
        'TurnedOn': 'turned_on',
        'TurnedOff': 'turned_off',
        'StateChanged': 'state_changed'
    }

class DeviceAction: # pylint: disable=too-few-public-methods
    """ supported Device Actions in Steps """
    TurnOn = 'turn_on'
    TurnOff = 'turn_off'
    Toggle = 'toggle'
    _as_dict = {
        'TurnOn': 'turn_on',
        'TurnOff': 'turn_off',
        'Toggle': 'toggle'
    }

class StepType: # pylint: disable=too-few-public-methods
    """ There are two kind of routine steps for now:
    - Delay, which has a parameter 'duration' in seconds
    - DeviceAction, which has two parameters: device: LexieDevice and action:str
    action param should be a LexieDeviceAction class, but later"""
    DeviceAction = 'device_action'
    Delay = 'delay'
    _as_dict = {
        'DeviceAction': 'device_action',
        'Delay': 'delay',
    }

class Step: #pylint: disable=too-few-public-methods
    """ represents an action that can be taken in a routine. This should include:
    - Device Control actions (for now: on/off)
    - delay
    Parameters: step_type: str (StepType.DeviceActin or StepType.Delay should be used)
                device: LexieDevice (optional)
                action: str (on/off for now, optional, must have id step_type==StepType.DeviceAction)
                duration: int (optional, must have if step_type == StepType.Delay"""

    def __init__(self, step_id: str) -> None:
        self.step_dict = fetch_from_db('step', step_id)
        self.step_type = self.step_dict['step_type']
        self.id = self.step_dict['id'] #pylint: disable=invalid-name
        if self.step_dict['next_step'] is None:
            self.next_step = None
        else:
            self.next_step = Step(self.step_dict['next_step'])
        if self.step_type == StepType.DeviceAction:
            self.device = LexieDevice(self.step_dict['device_id'])
            self.action = self.step_dict['device_action']
        elif self.step_type == StepType.Delay:
            self.delay_duration = self.step_dict['delay_duration']

    @staticmethod
    def new(step_type: str, device: LexieDevice = None, device_action: str = None, delay_duration: int = None):
        """ Creates and stores a new Step in TinyDB """
        # Verify parameters
        if (step_type == StepType.DeviceAction and # pylint: disable=too-many-boolean-expressions
                (device is None or
                device_action is None or
                delay_duration is not None)
            ) or (
                step_type == StepType.Delay and
                (device is not None or
                device_action is not None or
                delay_duration is None)
            ):
            raise InvalidParametersException('Bad parameter combination calling Step.new()')
        step_id = uuid()
        step_dict = {
            'id': step_id,
            'step_type': step_type,
            'next_step': None # all new steps are created without a next step. Next step must be added via add_next() method
        }
        if device is not None:
            step_dict['device_id'] = device.device_id
        if device_action is not None:
            step_dict['device_action'] = device_action
        if delay_duration is not None:
            step_dict['delay_duration'] = delay_duration
        push_to_db('step', step_dict)
        return Step(step_id=step_id)

    def __find_parent(self):
        """ looks for triggers/steps that have self as next_step """
        parent = search_in_db('trigger', 'next_step', self.id)
        if parent is not None:
            return Trigger(parent['id'])
        parent = search_in_db('step', 'next_step', self.id)
        if parent is None:
            return None
        return Step(parent['id'])

    def __remove_parent(self):
        """ searches the DB for parent step/trigger and removes reference """
        parent = self.__find_parent()
        if parent is not None:
            parent.remove_next()

    def delete(self):
        """ Deletes a step.
            First it checks if there's a next_step. If there is, step cannot be deleted,
            because it would break the chain of a Routine """
        if self.next_step is None:
            # Remove reference in parent
            self.__remove_parent()
            delete_from_db('step', self.id)
        else:
            parent = self.__find_parent()
            if parent is not None:
                parent.remove_next()
                parent.add_next(self.next_step)
            self.next_step = None
            delete_from_db('step', self.id)

    def add_next(self, next_step):
        """ adds a next step pointer """
        if self.next_step is None:
            self.next_step = next_step
            self.step_dict['next_step'] = next_step.id
            update_in_db('step', self.step_dict)
        else:
            raise NextStepAlreadyDefinedException('Cannot add next_step, next_step is already defined')

    def remove_next(self):
        """ removes next pointer """
        if self.next_step is not None:
            self.next_step = None
            self.step_dict['next_step'] = None
            update_in_db('step', self.step_dict)

    def execute(self):
        """ executes the Step """
        if self.step_type == StepType.Delay:
            time.sleep(self.delay_duration)
        elif self.step_type == StepType.DeviceAction:
            if self.action == DeviceAction.TurnOn:
                self.device.action_turn(True)
            elif self.action == DeviceAction.TurnOff:
                self.device.action_turn(False)
            elif self.action == DeviceAction.Toggle:
                self.device.action_toggle()

class TriggerType: # pylint: disable=too-few-public-methods
    """ there are currently two kind of triggers:
        DeviceEvent which triggers a routine if an device produces an event (a switch turned on, a sensor reporting some data)
        Timer which triggers a routine at a certain time of the day"""
    DeviceEvent = 'device_event'
    Timer = 'timer'
    _as_dict = {
        'DeviceEvent': 'device_event',
        'Timer': 'timer'
    }

class TriggerTimer:
    """ stores times when a Trigger with TriggerType.Timer should be fired """
    def __init__(self, timer_id) -> None:
        self.timer_dict = fetch_from_db('timer', timer_id)
        self.id = timer_id # pylint: disable=invalid-name
        self.schedules = self.timer_dict['schedules']

    @staticmethod
    def new():
        """ creates a new, empty timer """
        timer_id = uuid()
        timer_dict = {
            'id': timer_id,
            'schedules': []
        }
        push_to_db('timer', timer_dict)
        return TriggerTimer(timer_id)

    def add_schedule(self, hour: int, minute: int, day_of_week: str = "*"):
        """ adds one dow/hour/minute to the schedules """
        self.schedules.append(
            {
                'day_of_week': day_of_week,
                'hour': hour,
                'minute': minute
            }
        )
        self.timer_dict['schedules'] = self.schedules
        update_in_db('timer', self.timer_dict)

class Trigger: # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """ the first object in a routine. A Trigger starts a series of steps
        A Trigger is an event of a LexieDevice """
    def __init__(self, trigger_id) -> None:
        self.trigger_dict = fetch_from_db('trigger', trigger_id)
        self.id = self.trigger_dict['id'] #pylint: disable=invalid-name
        self.type = self.trigger_dict['type']
        self.next_step = self.trigger_dict['next_step']
        self.name = self.trigger_dict['name']
        self.enabled = self.trigger_dict['enabled']
        if self.type == TriggerType.DeviceEvent:
            self.device_id = self.trigger_dict['device_id']
            self.device = LexieDevice(self.trigger_dict['device_id'])
            self.event = self.trigger_dict['event']
        else:
            self.timer = TriggerTimer(self.trigger_dict['timer'])

    @staticmethod
    def new(name: str, trigger_type: str, device: LexieDevice = None, event: str = None, timer: TriggerTimer = None, enabled: bool=True): # pylint: disable=too-many-arguments
        """ Creates a new Trigger """
        trigger_id = uuid()
        if trigger_type == TriggerType.Timer:
            if timer is None:
                raise InvalidParametersException
            trigger_dict = {
                'id': trigger_id,
                'name': name,
                'type': TriggerType.Timer,
                'next_step': None,
                'enabled': enabled,
                'timer': timer.id
            }
            push_to_db('trigger', trigger_dict)
            trigger = Trigger(trigger_id)
            for ttimer in trigger.timer.schedules:
                if ttimer['day_of_week'] == 7:
                    ttimer['day_of_week'] = 0
                scheduler.add_job(
                    id='trigger_' + trigger_id + str(ttimer['day_of_week']),
                    func=fire_trigger,
                    args=[trigger_id],
                    trigger='cron',
                    day_of_week=ttimer['day_of_week'],
                    hour=ttimer['hour'],
                    minute=ttimer['minute']
                )
            return trigger
        if device is None or event is None:
            raise InvalidParametersException
        trigger_dict = {
            'id': trigger_id,
            'name': name,
            'type': TriggerType.DeviceEvent,
            'device_id': device.device_id,
            'event': event,
            'next_step': None,
            'enabled': enabled
        }
        push_to_db('trigger', trigger_dict)
        return Trigger(trigger_id)

    def delete(self):
        """ Deletes a trigger and the whole chain with it """
        if self.next_step is not None:
            current = self.last_in_chain()
            while current:
                if current.id == self.id:
                    current = None
                else:
                    current.delete()
                    temp_trigger = Trigger(self.id)
                    current = temp_trigger.last_in_chain()
        if self.type == TriggerType.Timer:
            try:
                for schedule in self.timer.schedules:
                    scheduler.remove_job('trigger_' + self.id + str(schedule['day_of_week']))
            except apscheduler.jobstores.base.JobLookupError: # pragma: nocover
                pass
        delete_from_db('trigger', self.id)

    def add_next(self, next_step: Step):
        """ adds the first step which should be executed on a trigger """
        if self.next_step is None:
            self.trigger_dict['next_step'] = next_step.id
            self.next_step = next_step.id
            update_in_db('trigger', self.trigger_dict)
        else:
            raise NextStepAlreadyDefinedException('Cannot add next_step, next_step is already defined')

    def remove_next(self):
        """ removes next step if exists """
        if self.next_step is not None:
            self.next_step = None
            self.trigger_dict['next_step'] = None
            update_in_db('trigger', self.trigger_dict)

    def last_in_chain(self):
        """ finds the last step of a routine """
        if self.next_step is None:
            return self
        current_step = Step(self.next_step)
        while current_step.next_step is not None:
            current_step = current_step.next_step
        return current_step

    def chain_to_list(self):
        """ returns a list with all the steps in the chain """
        if self.next_step is None:
            return []
        step_list = []
        current_step = Step(self.next_step)
        step_list.append(current_step)
        while current_step.next_step is not None:
            current_step = current_step.next_step
            step_list.append(current_step)
        return step_list

    def enable(self):
        """ enables trigger """
        self.enabled = True
        self.trigger_dict['enabled'] = True
        update_in_db('trigger', self.trigger_dict)

    def disable(self):
        """ disables trigger """
        self.enabled = False
        self.trigger_dict['enabled'] = False
        update_in_db('trigger', self.trigger_dict)

    @staticmethod
    def get_all():
        """ gets all triggers from database and returns a List of Trigger objects """
        all_triggers = fetch_all_from_db('trigger')
        triggers = []
        for db_trigger in all_triggers:
            triggers.append(Trigger(db_trigger['id']))
        return triggers

    def fire(self):
        """ looks up actions in steps and executes them """
        if self.next_step is not None and self.enabled:
            first_step = Step(self.next_step)
            first_step.execute()
            current_step = first_step.next_step
            while current_step:
                current_step.execute()
                current_step = current_step.next_step
