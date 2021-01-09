from abc import ABCMeta, abstractmethod
from typing import List

from .base_device import Device, DeviceAction


class UpdateConfig(DeviceAction):
    """
    Updates the configuration based on the specified arguments given
    """
    _name = 'update_config'
    _desc = """
        Updates the Device Configuration for the given arguments. 
    """

    def argmap(self) -> dict:
        return self.device.config.config_map()

    def perform(self):
        for key in self.args:
            self.device.config[key] = self.args[key]

        self.device.config.save()


class ConfigurableDevice(Device, metaclass=ABCMeta):
    """
    This class represents a Device with a saved Config file (probably most
    devices)

    _conf_class must be set in order to access the config
    """
    _conf_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = self._conf_class()

    @abstractmethod
    def actions(self) -> List[DeviceAction]:
        return super().actions() + [
            UpdateConfig(self)
        ]
