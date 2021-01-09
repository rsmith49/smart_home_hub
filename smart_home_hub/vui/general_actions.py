"""
This file contains all general DeviceActions that can be run without a
device, and at any time.
"""
from marshmallow import fields
from typing import List

from smart_home_hub.device.base_device import DeviceAction
from smart_home_hub.device.context_device import ContextDevice
from smart_home_hub.device import device_class_map


class ListDevices(DeviceAction):
    _name = 'list_devices'
    _desc = 'Lists the available devices'

    def argmap(self) -> dict:
        return {}

    def perform(self):
        self.set_msg(', '.join(device_class_map.keys()))


class EnterDevice(DeviceAction):
    _name = 'enter'
    _desc = 'Sets a device in the context, so you only have to say an action'

    def argmap(self) -> dict:
        return {
            'device_name': fields.Str(
                required=True,
                voice_ndx=0
            )
        }

    def perform(self):
        if self.device.context is None:
            self.set_msg('No context found')
            return

        self.device.context['device'] = self.args['device_name']
        self.device.save_context()

        self.set_msg(f'Using device {self.args["device_name"]}')


class ExitDevice(DeviceAction):
    _name = 'exit'
    _desc = 'Resets the context, removing the device'

    def argmap(self) -> dict:
        return {}

    def perform(self):
        if self.device.context is None:
            self.set_msg('No context found')
            return

        self.device.context.reset_content()
        self.device.save_context()


class GenericDevice(ContextDevice):
    """
    A generic Device class to use as the Device containing all generic actions
    """
    _name = 'generic_vui_device'

    def actions(self) -> List[DeviceAction]:
        # NOTE: We intentionally do not combine with super() here. Instead, we
        #       override the 'list' action
        return [
            ListDevices(self),
            EnterDevice(self),
            ExitDevice(self)
        ]
