from abc import ABCMeta, abstractmethod
from typing import Optional

from .base_device import Device
from smart_home_hub.utils.config_class import Config


class ContextDevice(Device, metaclass=ABCMeta):
    """
    A Device class that makes use of the current context (aka state of
    command history) to perform and show available actions.
    """
    def __init__(self, *args, context: Optional[Config] = None, **kwargs):
        """
        :param context: A dict of the current context given previous calls,
                        or None if no prior context.
        """
        super().__init__(*args, **kwargs)
        self.context = context

    def save_context(self):
        """
        Saves the current context object into the appropriate location
        """
        if self.context is not None:
            self.context.save()
