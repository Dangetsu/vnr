:: run.cmd
:: 11/1/2012 jichi
setlocal
set PATH=..\..\..\..\Qt\PySide;%PATH%
set PYTHON=..\..\..\..\Python\python.exe
::set FLAGS=-B -d -v
set FLAGS=-B
%PYTHON% %FLAGS% debug.py  --debug %*
