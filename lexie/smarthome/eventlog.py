from lexie.smarthome import models


def log(event:str):
    """ saves an event to Event Log """
    eventlog = models.EventLog(event=event)
    models.db.session.add(eventlog)
    models.db.session.commit()
