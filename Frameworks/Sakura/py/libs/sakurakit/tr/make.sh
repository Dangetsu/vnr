#!/bin/sh -v
# 8/31/2014 jichi
count=`ls *qm|wc -l`
echo make -j $count "$@"
make -j $count "$@"

# EOF
