#!/bin/sh -v
# 11/1/2012 jichi
export PATH=/opt/local/bin:$PATH
python .  --debug "$@"
