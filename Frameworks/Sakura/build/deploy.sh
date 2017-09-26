#!/bin/sh -v
# 9/19/2013
cd `dirname "$0"`

PYPLUGIN=pyvnrmem
FROM=../build/lib$PYPLUGIN.so
TO=../bin/$PYPLUGIN.so
rm -f "$TO"
ln -s "$FROM" "$TO"

QMLPACKAGE=texscript
QMLPLUGIN=${QMLPACKAGE}plugin
FROM=../../../build/lib$QMLPLUGIN.dylib
TO=../qml/imports/$QMLPACKAGE/lib$QMLPLUGIN.dylib
rm -f "$TO"
ln -s "$FROM" "$TO"

QMLPACKAGE=qmleffects
QMLPLUGIN=${QMLPACKAGE}plugin
FROM=../../../build/lib$QMLPLUGIN.dylib
TO=../qml/imports/$QMLPACKAGE/lib$QMLPLUGIN.dylib
rm -f "$TO"
ln -s "$FROM" "$TO"

QMLPACKAGE=qmlhelper
QMLPLUGIN=${QMLPACKAGE}plugin
FROM=../../../build/lib$QMLPLUGIN.dylib
TO=../qml/imports/$QMLPACKAGE/lib$QMLPLUGIN.dylib
rm -f "$TO"
ln -s "$FROM" "$TO"

# EOF
