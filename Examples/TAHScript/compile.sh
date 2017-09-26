#!/bin/sh
# tahcompile.sh
# 1/6/2015 jichi
cd "`dirname "$0"`"
export PATH=../../../Scripts:$PATH

echo "tahcompile.sh tah-*.txt -o output.txt"
exec tahcompile.sh tah-*.txt -o output.txt
