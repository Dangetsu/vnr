@echo off
:: coding: sjis, ff=dos
:: update.cmd
:: 11/12/2012 jichi
::
:: Note for wine:
:: - Leading redirection to nul is not supported
:: - :: lines are not hidden
setlocal
cd /d %~dp0
cd /d ../..

title Update
::color 8f

if not exist .gitignore (
  echo WARNING: Unknown library repository.
  exit /b 1
)

if exist Update/Scripts/initenv.cmd call Update/Scripts/initenv.cmd

::            1         2         3         4         5         6         7
echo ----------------------------------------------------------------------
echo                          Updating Sakura ...
echo ----------------------------------------------------------------------

taskkill /f /IM python 2>nul
taskkill /f /IM pythonw 2>nul
taskkill /f /IM 7za 2>nul
taskkill /f /IM hg 2>nul

set GIT=%CD%\Frameworks\Git\cmd\git.exe
"%GIT%" pull https://github.com/Dangetsu/vnr.git

echo ----------------------------------------------------------------------
echo                          Updating Sakura FINISH
echo ----------------------------------------------------------------------
