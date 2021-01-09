"""
This file contains environment defined constants that are set at the start
of the program
"""
import os

API_PORT = os.environ.get('SHH_API_PORT')
API_KEY = os.environ.get('SHH_API_KEY')

CONFIG_BASE_DIR = os.environ.get('SHH_CONFIG_BASE_DIR')
if CONFIG_BASE_DIR is None:
    CONFIG_BASE_DIR = 'config/'

try:
    MIC_DEVICE_NDX = int(os.environ.get('SHH_MIC_DEVICE_INDEX'))
except (TypeError, ValueError):
    MIC_DEVICE_NDX = None
