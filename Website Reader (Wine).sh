#!/bin/sh
# 9/28/2013 jichi
ME="`basename "$0" .sh`"
cd "`dirname "$0"`"

MACPORTS_HOME=/opt/local
DARWINE_HOME=/Applications/Wine.app/Contents/Resources
export PATH=$PATH:$MACPORTS_HOME/bin:$DARWINE_HOME/bin

die()
{
  >&2 echo "$@"
  exit 1
}

require()
{
  local i
  for i; do
    which "$i" >/dev/null 2>&1 || \
      die "$ME: cannot find '$i' in PATH, ABORT"
  done
}
require wine
WINE=wine

export LANG=ja_JP.UTF-8
export LC_ALL=ja_JP.UTF-8

#echo "$ME: wine cmd /c 'Debug Reader'"
#exec wine cmd /c "Debug Reader" "$@"

PYTHON=Frameworks/Python/python.exe
FLAGS=-B
APP=Frameworks/Sakura/py/apps/browser
APP_OPT=--debug
echo "$ME: $WINE $PYTHON $FLAGS $APP $APP_OPT $@"
exec $WINE "$PYTHON" $FLAGS "$APP" $APP_OPT "$@"

# EOF
