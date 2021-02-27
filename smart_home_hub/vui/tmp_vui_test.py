import os, sys

from dotenv import load_dotenv, find_dotenv

sys.path.append(os.getcwd())

# Loading environment variables before imports (in case any are env dependent)
load_dotenv(find_dotenv(raise_error_if_not_found=True, usecwd=True))

from smart_home_hub.vui.vui_thread import VUI
from smart_home_hub.vui.tts.basic_tts import BasicTTS
from smart_home_hub.vui.stt.pico_stt import PicoSTT


def main():
    vui = VUI(
        BasicTTS(debug=True),
        PicoSTT(debug=True)
    )
    vui.run()


if __name__ == '__main__':
    main()
