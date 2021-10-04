import json

from lexie.smarthome import models


def send_event(device_id,  event, event_type):
    """ puts an event to the queue """
    if event_type == 'status':
        event_data = {'event_type': 'status', 'event_data': event}
    db_event = models.Event(device_id=device_id, event=json.dumps(event_data))
    models.db.session.add(db_event)
    models.db.session.commit()
