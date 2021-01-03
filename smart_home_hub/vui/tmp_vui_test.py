import os, sys

sys.path.append(os.getcwd())

from smart_home_hub.vui.vui_thread import VUI
from smart_home_hub.vui.stt.basic_stt import BasicSTT
from smart_home_hub.vui.tts.basic_tts import BasicTTS


def main():
    vui = VUI(
        BasicTTS(debug=True),
        BasicSTT(debug=True)
    )
    vui.run()


if __name__ == '__main__':
    main()
