"""
This file contains the interfaces used for Speech to Text classes
that will be used with the VUI object
"""
from abc import ABCMeta, abstractmethod


class SpeechToText(metaclass=ABCMeta):

    @abstractmethod
    def listen_for_wakeword(self, wakeword):
        """
        Listens (waits) until a wakeword is spoken, then returns the entire
        string of spoken text
        """

    @abstractmethod
    def listen(self):
        """
        Listens and returns the audio spoken, having been converted to a string
        :return: A string record of the audio spoken
        """
