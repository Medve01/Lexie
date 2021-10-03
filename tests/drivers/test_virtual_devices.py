import pytest
from lexie.drivers.virtual.switch import HWDevice
# from tests.fixtures.test_flask_app import app

device_data={
                "device_id": "123456",
                "device_name": "Mock Virtual Switch",
                "device_attributes": None,
                "device_manufacturer": "virtual",
                "device_product": "switch",
                "device_type": 1
            }

def test_virtual_switch_init():
    testdevice = HWDevice(device_data=device_data)
    assert (
        testdevice.device_id == '123456' and
        testdevice.supports_events is True and
        testdevice.ison is True)

@pytest.mark.parametrize('onoff, result',
    [
        (True, {'online': True, 'ison': True}),
        (False, {'online': True, 'ison': False})
    ]
)
def test_virtual_switch_turn_onoff(onoff, result):
    """" tests turning on/off """
    testdevice = HWDevice(device_data=device_data)
    assert testdevice.action_turn(onoff) == result

def test_virtual_switch_toggle():
    testdevice = HWDevice(device_data=device_data)
    testdevice.action_turn(True)
    assert testdevice.action_toggle() == {'online': True, 'ison': False}
    testdevice.action_turn(False)
    assert testdevice.action_toggle() == {'online': True, 'ison': True}

def test_virtual_switch_get_status():
    testdevice = HWDevice(device_data=device_data)
    testdevice.action_turn(False)
    assert testdevice.get_status() == {'online': True, 'ison': False}

def test_virtual_switch_setup_events():
    testdevice = HWDevice(device_data=device_data)
    assert testdevice.setup_events() is True

