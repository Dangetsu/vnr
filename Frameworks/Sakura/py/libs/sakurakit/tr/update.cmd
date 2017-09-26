:: update.cmd
:: 2/17/2013 jichi
@setlocal
@echo off

set proj=../tr.pro

echo pyside-lupdate %proj%
pyside-lupdate %proj%
dos2unix *

:: EOF
