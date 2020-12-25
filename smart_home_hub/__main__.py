import os
import requests
import sys
import threading
import time

from dotenv import load_dotenv, find_dotenv
from queue import Queue

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
    target=lambda x: None
)

# Methods to use
q = Queue()

task = 0
q.put(task)

q.get()
q.task_done()

q.join()

# Continue actual stuff

api_thread.run()
vui_thread.run()

# Main loop
try:
    while True:
        time.sleep(2)
except KeyboardInterrupt:
    pass

# On shutdown
requests.post(
    f'http://localhost:{API_PORT}/shutdown'
)

api_thread.join()
vui_thread.join()
