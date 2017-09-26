# coding: utf8
# 5/28/2014
path = 'zunko.yaml'

import yaml
with open(path) as f:
  data = f.read()
yaml.load(data)

# EOF
