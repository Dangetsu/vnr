:: run.cmd
:: 11/1/2012 jichi
setlocal
set PYTHON=..\..\..\..\Python\python.exe

set VIDS=XGZ2S6pTkO8 lmOZEAAEMK0
set LOCATION=%USERPROFILE%/Desktop/test

%PYTHON% . "%LOCATION%" %VIDS%  --debug %*
