#!/bin/sh -v
# 11/1/2012 jichi
cd "`dirname "$0"`"
export PATH="/opt/local/bin:$PATH"
export PYTHONPATH=/opt/local/lib/python2.7/site-packages:$PYTHONPATH
export LD_LIBRARY_PATH=$PWD/../../../../EB/build:$LD_LIBRARY_PATH
export DYLD_LIBRARY_PATH=$PWD/../../../../EB/build:$DYLD_LIBRARY_PATH
echo $DYLD_LIBRARY_PATH
python debug.py  --debug "$@"

# EOF
