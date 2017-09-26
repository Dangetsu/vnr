:: Kill Python.cmd
:: 9/29/2013 jichi
:: Kill all python processes.
@echo off
setlocal

title Kill Python

echo.
echo taskkill /f /IM python
taskkill /f /IM python

echo.
echo taskkill /f /IM pythonw
taskkill /f /IM pythonw

::echo.
::echo taskkill /f /IM hg
::taskkill /f /IM hg

echo.
pause

:: EOF
