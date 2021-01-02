from abc import ABCMeta, abstractmethod
from copy import deepcopy
from marshmallow import fields
from typing import List

from ..utils.utils import DescClass


class DeviceAction(DescClass, metaclass=ABCMeta):
    # TODO: I think we need to make the __init__ actually not take any arguments,
    # and just have an additional method init() that argmap args are passed to before perform
    """
    An Action that can be taken on a device. Specifies what arguments can
    be given, and what response will occur.

    These objects will be used by devices to be interacted with via the 2 main
    control options (API & VUI).

    _name must be specified (and be unique)
    _desc can be specified to give information on the action performed.
    """
    def __init__(self, device):
        super().__init__()
        self.device = device
        self.args = {}
        self.resp = {
            'message': ''
        }

    def init_args(self, **kwargs):
        """
        Initializes the action with any args passed
        (these args are specified by the argmap)
        """
        # TODO: Some kind of argument check here that the args are from argmap
        self.args = deepcopy(kwargs)

    @abstractmethod
    def argmap(self) -> dict:
        """
        Returns a dict containing marshmallow fields on what type of arguments
        are expected to call this action (will be passed to constructor)
        """
        return {}

    def response(self) -> dict:
        """
        Returns a JSON serializable dict, which must include 'message' as
        a key.
        """
        return self.resp

    def set_msg(self, new_msg):
        """
        Sets the message of the response with a new string
        """
        self.resp['message'] = new_msg

    @abstractmethod
    def perform(self):
        """
        Performs the action. Main code goes here.

        NOTE: Should also set self.resp here, unless you want to override
              self.response()
        """


class ListActions(DeviceAction):
    """
    An action that all devices should have, which lists the actions available
    to the device in the response.
    """
    _name = 'list_actions'

    def argmap(self) -> dict:
        return {}

    def perform(self):
        self.set_msg(
            ', '.join(self.device.action_names())
        )


class ListActionArgs(DeviceAction):
    """
    An action that all devices should have, which lists the arguments available
    to the action specified.
    """
    _name = 'list_arguments'

    def argmap(self):
        return {
            'action': fields.Str(
                required=True,
                voice_ndx=0
            )
        }

    def perform(self):
        # TODO: Make this better? Aka maybe list the requirements too and stuff
        self.set_msg(
            ', '.join(
                self.device.action_map()[
                    self.args['action'].lower()
                ].argmap().keys()
            )
        )


class Device(DescClass, metaclass=ABCMeta):
    """
    Device class that is used for interacting with a device. Contains
    information (usually URL's and any API keys) for contacting the device,
    and a list of actions that can be performed.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def dev_name(cls):
        return cls._name

    @classmethod
    def dev_desc(cls):
        return cls._desc

    @abstractmethod
    def actions(self) -> List[DeviceAction]:
        """
        Should return a list of all available actions for this device
        """
        return [
            ListActions(self),
            ListActionArgs(self)
        ]

    def action_names(self) -> List[str]:
        """
        Returns a list of the action names for the device
        """
        return [
            action.name for action in self.actions()
        ]

    def action_map(self):
        """
        Returns a map of name: Action pairs for this device
        """
        action_map = {}

        for action in self.actions():
            if action.name in action_map:
                raise ValueError(f'Non-unique name {action.name} for Action')

            action_map[action.name] = action

        return action_map
