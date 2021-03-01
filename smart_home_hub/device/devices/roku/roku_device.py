import os

from typing import List, Union

from .keypress_actions import Volume, Home, PowerOn, PowerOff, HDMI, Select
from .discover_ip import SetIP
from .content_actions import PlayRandom, PlayContent, PlayMovie, PlayShow
from .reelgood_client import RGClient
from smart_home_hub.device.base_device import DeviceAction
from smart_home_hub.device.configurable_device import ConfigurableDevice
from smart_home_hub.device.context_device import ContextDevice
from smart_home_hub.utils.config import Config, ConfigMap

RG_EMAIL_ENV = 'SHH_RG_EMAIL'
RG_PASSWORD_ENV = 'SHH_RG_PASS'


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.rg_client = RGClient(
                email=os.environ[RG_EMAIL_ENV],
                password=os.environ[RG_PASSWORD_ENV]
            )
        except KeyError:
            # We will not include RG related functionality
            self.rg_client = None

    def actions(self) -> List[DeviceAction]:
        _actions = super().actions() + [
            SetIP(self),
            Volume(self),
            Home(self),
            PowerOn(self),
            PowerOff(self),
            HDMI(self),
            Select(self),
            PlayRandom(self),
            PlayContent(self)
        ]

        if self.rg_client is not None:
            _actions += [
                PlayMovie(self),
                PlayShow(self)
            ]

        return _actions
