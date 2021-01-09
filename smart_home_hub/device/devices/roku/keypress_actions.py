"""
This file contains classes representing basic device actions for imitating
useful keypresses on the roku remote (bc I am lazy)
"""
import requests

from abc import ABCMeta
from marshmallow import fields, validate

from smart_home_hub.device.base_device import DeviceAction


def keypress_endpoint(event) -> str:
    """
    Helper method to return the endpoint for the corresponding keypress event
    :param event: Name of the event (ex: powerOn/powerOff)
    :return: A string of the URL to hit
    """
    return f'/keypress/{event}'


class KeyPressAction(DeviceAction, metaclass=ABCMeta):
    """
    Helper class to make the accessing of endpoints less hardcoded
    """
    def keypress(self, event):
        requests.post(self.device.config['ip'] + keypress_endpoint(event))


class Volume(KeyPressAction):
    _name = 'volume'

    def argmap(self) -> dict:
        return {
            'direction': fields.Str(
                required=True,
                voice_ndx=0,
                validate=validate.OneOf(['up', 'down'])
            ),
            'units': fields.Int(
                missing=1,
                voice_ndx=1
            )
        }

    def perform(self):
        for _ in range(self.args['units']):
            if self.args['direction'] == 'up':
                event = 'volumeUp'
            else:
                event = 'volumeDown'

            self.keypress(event)


class Home(KeyPressAction):
    _name = 'home'

    def argmap(self):
        return {}

    def perform(self):
        self.keypress('Home')


class PowerOn(KeyPressAction):
    _name = 'on'

    def argmap(self):
        return {}

    def perform(self):
        self.keypress('powerOn')


class PowerOff(KeyPressAction):
    _name = 'off'

    def argmap(self):
        return {}

    def perform(self):
        self.keypress('powerOff')


class OK(KeyPressAction):
    _name = 'ok'

    def argmap(self) -> dict:
        return {}

    def perform(self):
        self.keypress('Select')


class HDMI(KeyPressAction):
    _name = 'hdmi'

    def argmap(self):
        return {
            'input': fields.Int(
                required=True,
                voice_ndx=0
            )
        }

    def perform(self):
        self.keypress(
            f"InputHDMI{self.args['input']}"
        )
