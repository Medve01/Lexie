import pytest
from lexie.devices.device import LexieDevice

def test_device():
    device_id = '1234'
    testdevice = LexieDevice(device_id)

    assert testdevice.device_id == device_id

def test_device_status():
    device_id='1234'
    testdevice = LexieDevice(device_id)
    status = testdevice.status()
    assert status['device_id'] == device_id
    assert (status['online'] is True) or (status['online'] is False)
    assert (status['ison'] is True) or (status['ison'] is False)
   