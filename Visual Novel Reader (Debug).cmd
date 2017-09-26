:: Visual Novel Reader (Debug).cmd
:: 11/1/2012 jichi
@echo off
setlocal

cd /d %~dp0/..

title Visual Novel Reader (Debug)
::color 8f

set ME=Debug

set PYTHON=Library\Frameworks\Python\python.exe
set FLAGS=-B
set PYTHON_OPT=
set SCRIPT=Library/Frameworks/Sakura/py/apps/reader
set SCRIPT_OPT=--debug

set PATH=%windir%;%windir%\system32

echo %ME%: PWD = %CD%
echo %ME%: %PYTHON% %FLAGS% %PYTHON_OPT% %SCRIPT% %SCRIPT_OPT% %*
echo.
%PYTHON% %FLAGS% %PYTHON_OPT% %SCRIPT% %SCRIPT_OPT% %*
set ret=%ERRORLEVEL%
echo.
echo %ME%: exit code: %ret%

echo.
pause

:: EOF
