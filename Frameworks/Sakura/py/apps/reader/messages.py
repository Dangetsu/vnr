# coding: utf8
# messages.py
# 11/28/2012 jichi

import config, rc

# Load yaml

YAML_LOCATION = rc.yaml_path('messages')
YAML = config.load_yaml_file(YAML_LOCATION)

# Greetings

GREETINGS_DAY = YAML['greetings']['day']
GREETINGS_MORNING = YAML['greetings']['morning']
GREETINGS_EVENING = YAML['greetings']['evening']

# EOF
