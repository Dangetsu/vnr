@echo off
:: coding: sjis, ff=dos
:: updateui.cmd
:: 3/17/2014 jichi
setlocal
cd /d %~dp0

title Update
::color 8f


::            1         2         3         4         5         6         7
echo ----------------------------------------------------------------------
echo       Do you want to update now? Internet connection is required.
echo ----------------------------------------------------------------------
echo.
pause
echo.

call update.cmd

echo.
pause

:: EOF
