"""
This file contains all general DeviceActions that can be run without a
device, and at any time.
"""
from typing import List

from smart_home_hub.devices.base_device import Device, DeviceAction
from smart_home_hub.devices import device_class_map


class ListDevices(DeviceAction):
    _name = 'list'

    def argmap(self) -> dict:
        return {}

    def perform(self):
        self.set_msg(', '.join(device_class_map.keys()))


class GenericDevice(Device):
    """
    A generic Device class to use as the Device containing all generic actions
    """
    _name = 'generic_vui_device'

    def actions(self) -> List[DeviceAction]:
        # NOTE: We intentionally do not combine with super() here. Instead, we
        #       override the 'list' action
        return [
            ListDevices(self)
        ]
