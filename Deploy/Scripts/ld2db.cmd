:: ld2db.cmd
:: 2/18/2015 jichi
:: Convert Lingoes LD2 dictionary to SQLite.
@echo off
setlocal

title sublint
::color 8f

set PYTHON=%~dp0\..\Library\Frameworks\Python\python.exe
set PYTHON_OPT=-B
set SCRIPT=%~dp0/../Library/Frameworks/Sakura/py/Scripts/ld2db.py
set SCRIPT_OPT=
::set SCRIPT_OPT=--debug

set PATH=%windir%;%windir%\system32

"%PYTHON%" %PYTHON_OPT% "%SCRIPT%" %SCRIPT_OPT% %*

echo.
pause

:: EOF
