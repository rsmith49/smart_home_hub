#!/bin/bash

git checkout main --quiet
git pull --quiet
source env/bin/activate
nohup python3 smart_home_hub/vui/tmp_vui_test.py > log.out &

