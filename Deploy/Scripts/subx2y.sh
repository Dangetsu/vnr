#!/bin/sh
# subx2y.sh
# 12/16/2014 jichi
# Convert VNR XML subtitle to YAML format.
CWD=`dirname "$0"`

PYTHON=python
PYTHON_OPT=-B
SCRIPT=$CWD/../Library/Frameworks/Sakura/py/Scripts/subx2y.py
SCRIPT_OPT=

exec $PYTHON $PYTHON_OPT "$SCRIPT" $SCRIPT_OPT "$@"
