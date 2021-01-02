"""
MVP for speech to text using basic SpeechRecognition classes
"""
import speech_recognition as sr

from .base_stt import SpeechToText


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
            result = self._listen(self.wakeword_rec_func).lower()
            if wakeword.lower() not in result:
                result = None

    def listen(self):
        return self._listen(self.transcribe_rec_func)

    def _listen_once(self, recognize_func):
        """
        Helper method to listen to one segment of sound, then return that
        chunk as text, or raise an sr.UnknownValueError
        :param recognize_func: A function that returns the interpreted str
                               given a recognizer and audio
        """
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
            return recognize_func(recognizer, audio)

    def _listen(self, recognize_func):
        """
        Listens and returns the audio using the specified recognize_func
        """
        result = None

        while result is None:
            try:
                result = self._listen_once(recognize_func)
            except sr.UnknownValueError:
                pass

        if self.debug:
            print('Recognized: {}'.format(result))

        return result
