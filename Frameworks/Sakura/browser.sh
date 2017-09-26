#!/bin/sh -v
# 11/1/2012 jichi
cd "`dirname "$0"`"
export PATH="/opt/local/bin:$PATH"
export PYTHONPATH=/opt/local/lib/python2.7/site-packages:$PYTHONPATH
APP=`basename "$0" .sh`
PYTHON=python
$PYTHON  py/apps/$APP --debug "$@"
