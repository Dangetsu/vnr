#!/bin/sh
# ld2db.py
# 2/18/2015 jichi
# Convert Lingoes LD2 dictionary to SQLite.
CWD=`dirname "$0"`

PYTHON=python
PYTHON_OPT=-B
SCRIPT=$CWD/../Library/Frameworks/Sakura/py/Scripts/ld2db.py
SCRIPT_OPT=
exec $PYTHON $PYTHON_OPT "$SCRIPT" $SCRIPT_OPT "$@"
