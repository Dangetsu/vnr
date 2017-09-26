:: tahcompile.cmd
:: 1/6/2015 jichi
:: Compile TAH script.
@echo off
setlocal

title tahcompile
::color 8f

set PYTHON=%~dp0\..\Library\Frameworks\Python\python.exe
set PYTHON_OPT=-B
set SCRIPT=%~dp0/../Library/Frameworks/Sakura/py/Scripts/tahcompile.py
set SCRIPT_OPT=
::set SCRIPT_OPT=--debug

set PATH=%windir%;%windir%\system32

"%PYTHON%" %PYTHON_OPT% "%SCRIPT%" %SCRIPT_OPT% %*

echo.
pause

:: EOF
