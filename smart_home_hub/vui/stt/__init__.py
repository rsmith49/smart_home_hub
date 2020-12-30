"""
This module contains code for dealing with Text-To-Speech needs
"""

# NOTE: For Deepspeech in the VAD demo file - we will need to have the previous
#       set of frames ready, and attach it to the start of the audio to
#       transcribe once VAD triggers
# NVM:  I think we figured it out - just need separate enter & exit ratios
from .base_stt import SpeechToText
from .parser import CommandParser
