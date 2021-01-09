#!/bin/sh
sudo apt-get update
sudo apt-get install python-scipy libatlas-base-dev python-pyaudio flac

# For pygame audio
sudo apt-get install libsdl2-mixer-2.0.0

# For Pocketsphinx
sudo apt-get install swig libpulse-dev libasound2-dev

# Create and source venv
python3 -m venv env
source env/bin/activate

# Install pip requirements
pip install --upgrade pip
pip install wheel
pip install -r requirements

# Set up SHH environment
python3 bin/setup_env_file.py
python3 bin/init_config_dir.py
