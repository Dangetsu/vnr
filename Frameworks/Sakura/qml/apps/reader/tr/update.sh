#!/bin/bash
# update.sh
# 11/5/2012 jichi
cd "$(dirname "$0")"

pro=../reader.pro

echo "lupdate '$pro'"
lupdate "$pro"

# EOF
