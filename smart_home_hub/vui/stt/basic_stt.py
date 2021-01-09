"""
MVP for speech to text using basic SpeechRecognition classes
"""
import speech_recognition as sr

from .base_stt import SpeechToText
from smart_home_hub.utils.env_consts import MIC_DEVICE_NDX


class BasicSTT(SpeechToText):

    def __init__(self, debug=False):
        self.debug = debug

        self.wakeword_rec_func = lambda r, a: r.recognize_sphinx(a)
        self.transcribe_rec_func = lambda r, a: r.recognize_google(a)

    def listen_for_wakeword(self, wakeword):
        """
        Listens until a wakeword is spoken using the pocketsphinx recognizer
        :param wakeword: Word (or phrase) to wait until is spoken
        """
        result = None

        while result is None:
            result = self._listen(
                self.wakeword_rec_func,
                phrase_time_limit=3.5
            ).lower()
            if wakeword.lower() not in result:
                result = None

    def listen(self):
        return self._listen(
            self.transcribe_rec_func,
            phrase_time_limit=7
        )

    def _listen_once(self, recognize_func, **listen_args):
        """
        Helper method to listen to one segment of sound, then return that
        chunk as text, or raise an sr.UnknownValueError
        :param recognize_func: A function that returns the interpreted str
                               given a recognizer and audio
        """
        recognizer = sr.Recognizer()
        with sr.Microphone(MIC_DEVICE_NDX) as source:
            if self.debug:
                print('Listening...')

            audio = recognizer.listen(source, **listen_args)

            if self.debug:
                print('Waiting on recognizer...')

            return recognize_func(recognizer, audio)

    def _listen(self, recognize_func, **listen_args):
        """
        Listens and returns the audio using the specified recognize_func
        """
        result = None

        while result is None:
            try:
                result = self._listen_once(recognize_func, **listen_args)
            except sr.UnknownValueError:
                pass

        if self.debug:
            print('Recognized: {}'.format(result))

        return result
