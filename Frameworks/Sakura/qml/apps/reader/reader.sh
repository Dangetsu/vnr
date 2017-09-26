#!/bin/sh
# 10/9/2012
# For debug only.

OS=`uname -s`
case `uname -s` in
Darwin) EXEC='open -a qmlviewer' ;;
*)      EXEC='exec qmlviewer'
esac

echo "os:\t$OS"
echo "run:\t$EXEC springboard.qml"
$EXEC springboard.qml

# EOF
