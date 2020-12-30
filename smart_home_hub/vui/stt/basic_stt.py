"""
MVP for speech to text using basic SpeechRecognition classes
"""
import speech_recognition as sr

from .base_stt import SpeechToText


class BasicTTS(SpeechToText):

    def __init__(self, debug=False):
        self.debug = debug

    def listen_for_wakeword(self, wakeword):
        result = None

        while result is None:
            result = self.listen().lower()
            if wakeword.lower() not in result:
                result = None

    def _listen_once(self):
        """
        Helper method to listen to one segment of sound, then return that
        chunk as text, or raise an sr.UnknownValueError
        """
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
            return recognizer.recognize_google(audio)

    def listen(self):
        result = None

        while result is None:
            try:
                result = self._listen_once()
            except sr.UnknownValueError:
                pass

        if self.debug:
            print('Recognized: {}'.format(result))

        return result
