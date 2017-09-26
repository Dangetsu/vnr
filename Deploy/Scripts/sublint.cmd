:: sublint.cmd
:: 12/16/2014 jichi
:: Validate VNR YAML subtitle format.
@echo off
setlocal

title sublint
::color 8f

set PYTHON=%~dp0\..\Library\Frameworks\Python\python.exe
set PYTHON_OPT=-B
set SCRIPT=%~dp0/../Library/Frameworks/Sakura/py/Scripts/sublint.py
set SCRIPT_OPT=
::set SCRIPT_OPT=--debug

set PATH=%windir%;%windir%\system32

"%PYTHON%" %PYTHON_OPT% "%SCRIPT%" %SCRIPT_OPT% %*

echo.
pause

:: EOF
