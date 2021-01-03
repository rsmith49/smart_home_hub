"""
MVP for text to speech using gtts and pygame
"""
import pygame
import time
import os

from gtts import gTTS

from .base_tts import TextToSpeech

TMP_TTS_FILENAME = '_tmp_tts_.mp3'


def audio_fname(text):
    """
    Function that converts a piece of text to the appropriate filename where
    the audio mp3 will be cached.
    """
    return f'audio_{hash(text)}.mp3'


def pygame_play(fname):
    """
    Plays the sound from the specified mp3 file through pygame
    """
    pygame.mixer.init()
    pygame.mixer.music.load(fname)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.2)


class BasicTTS(TextToSpeech):
    """
    A basic implementation of text to speech, that utilizes gTTS to transcribe
    text to audio files, then uses pygame to play those files.

    NOTE: It also caches the audio files to avoid re-querying gTTS too often
    """

    def __init__(self, debug=False, audio_file_dir='_tmp_audio_', cache_size=10):
        self.debug = debug

        self.audio_dir = audio_file_dir
        if self.audio_dir[-1] != '/':
            self.audio_dir += '/'

        try:
            for fname in os.listdir(self.audio_dir):
                os.remove(self.audio_dir + fname)
        except FileNotFoundError:
            os.mkdir(self.audio_dir)

        # Making an audio file cache to cut down on constant calls to gTTS
        self.file_cache = []
        self.cache_size = cache_size

    def recognize_wakeword(self):
        self.speak('Listening')

    def speak(self, text):
        if len(text) == 0:
            # No text to speak, gTTS will throw an error
            return

        fname = self.audio_dir + audio_fname(text)

        if fname in self.file_cache:
            self.file_cache.insert(
                0,
                self.file_cache.pop(
                    self.file_cache.index(fname)
                )
            )
        else:
            gTTS(text).save(fname)

            # Cache stuff
            self.file_cache.insert(0, fname)
            if len(self.file_cache) > self.cache_size:
                old_fname = self.file_cache.pop(-1)
                os.remove(old_fname)

        pygame_play(fname)
