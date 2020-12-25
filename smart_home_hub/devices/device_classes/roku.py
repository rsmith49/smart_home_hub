import requests
import upnpclient

from marshmallow import fields
from typing import List, Union

from ..base_device import DeviceAction
from ..configurable_device import ConfigurableDevice
from ..context_device import ContextDevice
from smart_home_hub.utils.config_class import Config, ConfigMap


def keypress_endpoint(event) -> str:
    """
    Helper method to return the endpoint for the corresponding keypress event
    :param event: Name of the event (ex: powerOn/powerOff)
    :return: A string of the URL to hit
    """
    return f'/keypress/{event}'


def list_available_devices() -> list:
    """
    Method to return list of available device names on the network
    """
    devices = upnpclient.discover()

    return [d.friendly_name for d in devices]


def discover_ip(device_name) -> str:
    """
    Method to return the URL (IP) to send requests to for a roku device of
    the given name
    :param device_name: Name of device we are searching for
    :return: An IP address string that can be used to send requests
    :raises: ValueError if no such device is found
    """
    devices = upnpclient.discover()

    roku_device = [
        d for d in devices
        if device_name.lower() == d.friendly_name.lower()
    ]

    if len(roku_device) == 0:
        raise ValueError(f'No device found for name {device_name}')

    return roku_device[0].location


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


class SetIP(DeviceAction):
    _name = 'set_device_ip'
    _desc = """
        Sets the Roku device IP based on the available devices on this network.
        If no device matching the name can be discovered, or if device_name is
        null, will return a list of available devices on the network.
    """

    def argmap(self) -> dict:
        return {
            'device_name': fields.Str(missing=None)
        }

    def perform(self):
        name = self.args['device_name']

        if name is not None:
            try:
                self.device.config['ip'] = discover_ip(name)
                self.device.config.save()
                return
            except ValueError:
                # Continuing to return list of available devices
                self.resp['message'] = f'Could not find device {name}. '

        available_devices = list_available_devices()
        self.resp['available_devices'] = available_devices
        self.resp['message'] += f'Available Device Names: {", ".join(available_devices)}'


class Volume(DeviceAction):
    _name = 'volume'

    def argmap(self) -> dict:
        return {
            'raise': fields.Bool(
                required=True,
                voice_ndx=0
            ),
            'units': fields.Int(
                missing=1,
                voice_ndx=1
            )
        }

    def perform(self):
        for _ in range(self.args['units']):
            if self.args['raise']:
                endpoint = keypress_endpoint('volumeUp')
            else:
                endpoint = keypress_endpoint('volumeDown')

            requests.post(self.device.config['ip'] + endpoint)


class RokuDevice(ContextDevice, ConfigurableDevice):
    """
    Represents a Roku Device we can interface with
    """
    _name = "roku"
    _desc = """
        A way to interact with any Roku devices on this network.
    """
    _conf_class = RokuConfig

    def actions(self) -> List[DeviceAction]:
        return super().actions() + [
            SetIP(self),
            Volume(self)
        ]
