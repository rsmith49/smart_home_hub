from abc import ABCMeta, abstractmethod

from .base_device import Device


class ContextDevice(Device, metaclass=ABCMeta):
    """
    A Device class that makes use of the current context (aka state of
    command history) to perform and show available actions.
    """
    def __init__(self, *args, context=None, **kwargs):
        """
        :param context: A dict of the current context given previous calls,
                        or None if no prior context.
        """
        super().__init__(*args, **kwargs)
        self.context = context
