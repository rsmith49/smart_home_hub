import pvporcupine
import pyaudio
import struct

from .basic_stt import BasicSTT
from smart_home_hub.utils.env_consts import MIC_DEVICE_NDX


class PicoSTT(BasicSTT):
    """
    Class that uses most of BasicSTT functionality, but has pvporcupine as the
    wakeword detection engine instead.
    """

    def __init__(self, *args, wakewords='jarvis', **kwargs):
        super().__init__(*args, **kwargs)

        if type(wakewords) is not list:
            wakewords = [wakewords]
        self.wakewords = wakewords

        self.handle = pvporcupine.create(
            keywords=wakewords
        )

    def listen_for_wakeword(self, wakeword):
        if wakeword.lower() not in self.wakewords:
            raise ValueError(f"Wakeword {wakeword} not supported")

        pa = pyaudio.PyAudio()

        audio_stream = pa.open(
            rate=self.handle.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.handle.frame_length,
            input_device_index=MIC_DEVICE_NDX
        )

        while True:
            pcm = audio_stream.read(self.handle.frame_length)
            pcm = struct.unpack_from("h" * self.handle.frame_length, pcm)
            result = self.handle.process(pcm)

            if result >= 0:
                if self.debug:
                    print('Wakeword detected')

                audio_stream.close()
                audio_stream.stop_stream()
                pa.terminate()
                return
