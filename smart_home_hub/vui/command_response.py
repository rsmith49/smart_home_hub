from abc import ABCMeta, abstractmethod


class CommandResponse(metaclass=ABCMeta):
    """
    A class to process and respond to a text command
    """
    def __init__(self, command):
        self.command = command
