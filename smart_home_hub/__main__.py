import os
import requests
import sys
import threading
import time  # Note: Get rid of this import once VUI is set up

from dotenv import load_dotenv, find_dotenv

sys.path.append(os.getcwd())

# Loading environment variables before imports (in case any are env dependent)
load_dotenv(find_dotenv(raise_error_if_not_found=True, usecwd=True))

from .api.api import app
from .utils.env_consts import API_PORT


api_thread = threading.Thread(
    target=app.run,
    kwargs={
        'host': '0.0.0.0',
        'port': API_PORT,
        'debug': False,
        'threaded': False
    },
    daemon=True
)
vui_thread = threading.Thread(
    target=lambda x: time.sleep(5)
)

api_thread.run()
vui_thread.run()

# Main loop
while True:
    break

# On shutdown
requests.post(
    f'http://localhost:{API_PORT}/shutdown'
)

api_thread.join()
vui_thread.join()
