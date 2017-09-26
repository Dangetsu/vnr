#!/bin/sh -v
# 11/1/2012 jichi
cd "`dirname "$0"`"
export PATH=/opt/local/bin:$PATH
PYTHON=python
$PYTHON .  --debug "$@"
