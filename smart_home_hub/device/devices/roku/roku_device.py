from typing import List, Union

from .keypress_actions import Volume, Home, PowerOn, PowerOff, HDMI
from .discover_ip import SetIP
from .content_actions import PlayRandom, PlayContent
from smart_home_hub.device.base_device import DeviceAction
from smart_home_hub.device.configurable_device import ConfigurableDevice
from smart_home_hub.device.context_device import ContextDevice
from smart_home_hub.utils.config import Config, ConfigMap


class RokuConfig(Config):
    """
    Internal config for Roku to use - has no keys to update directly from a
    request
    """

    def rel_filepath(self) -> str:
        return 'roku/main_config.json'

    @classmethod
    def config_map(cls) -> Union[ConfigMap, dict]:
        return {}


class RokuDevice(ContextDevice, ConfigurableDevice):
    """
    Represents a Roku Device we can interface with
    """
    _name = "roku"
    _desc = "A way to interact with any Roku devices on this network."

    _conf_class = RokuConfig

    def actions(self) -> List[DeviceAction]:
        return super().actions() + [
            SetIP(self),
            Volume(self),
            Home(self),
            PowerOn(self),
            PowerOff(self),
            HDMI(self),
            PlayRandom(self),
            PlayContent(self)
        ]
