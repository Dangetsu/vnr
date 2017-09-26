#!/bin/sh -v
# 9/19/2013
cd `dirname "$0"`

rm -f ../site-packages/eb.so
ln -s ../build/libebmodule.so ../site-packages/eb.so

rm -f ../site-packages/libeb.1.dylib
ln -s ../build/libeb.1.dylib ../site-packages/libeb.1.dylib

# EOF
