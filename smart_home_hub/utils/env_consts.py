"""
This file contains environment defined constants that are set at the start
of the program
"""
import os

API_PORT = os.environ.get('SHH_API_PORT')
API_KEY = os.environ.get('SHH_API_KEY')
CONFIG_BASE_DIR = os.environ.get('SHH_CONFIG_BASE_DIR')
