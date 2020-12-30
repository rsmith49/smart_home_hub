import os, sys

sys.path.append(os.getcwd())

from smart_home_hub.vui.vui_thread import VUI
from smart_home_hub.vui.stt.basic_stt import BasicTTS


def main():
    vui = VUI(print, BasicTTS(debug=True))
    vui.run()


if __name__ == '__main__':
    main()
