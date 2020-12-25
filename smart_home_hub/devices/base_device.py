from abc import ABCMeta, abstractmethod
from copy import deepcopy
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

    @abstractmethod
    def perform(self):
        """
        Performs the action. Main code goes here.

        NOTE: Should also set self.resp here, unless you want to override
              self.response()
        """


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
        return []

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
