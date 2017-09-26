#!/bin/sh
# tahcompile.sh
# 1/6/2015 jichi
CWD=`dirname "$0"`

PYTHON=python
PYTHON_OPT=-B
SCRIPT=$CWD/../Library/Frameworks/Sakura/py/Scripts/tahcompile.py
SCRIPT_OPT=

exec $PYTHON $PYTHON_OPT "$SCRIPT" $SCRIPT_OPT "$@"
