from abc import ABCMeta, abstractmethod


class TextToSpeech(metaclass=ABCMeta):
    """
    This class represents an interface for the VUI to use in responding
    to user commands.
    """

    @abstractmethod
    def recognize_wakeword(self):
        """
        Play the audio clip for having recognized the wakework/phrase
        """

    @abstractmethod
    def speak(self, text):
        """
        Converts the given text to an audio clip, and plays it over the
        microphone
        :param text: A string of text to play
        """
