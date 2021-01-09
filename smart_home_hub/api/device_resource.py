from smart_home_hub.device.base_device import Device, DeviceAction
from .utils import argmap_resp_obj


def action_resp_obj(action: DeviceAction) -> dict:
    """
    Returns a JSON compatible version of a DeviceAction object
    """
    return {
        'name': action.name,
        'description': action.description,
        'argmap': argmap_resp_obj(action.argmap())
    }


def device_resp_obj(device: Device) -> dict:
    """
    Returns a JSON compatible version of a device object to include in a
    response
    """
    return {
        'name': device.name,
        'description': device.description,
        'actions': [
            action_resp_obj(a) for a in device.actions()
        ],
        'action_map': {
            a_name: action_resp_obj(a)
            for a_name, a in device.action_map().items()
        }
    }
