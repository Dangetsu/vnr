:: compile.cmd
:: 1/6/2014 jichi
:: Generate TAH script to output.txt from tah-*.txt.
@echo off
setlocal
cd /d %~dp0
set PATH=%CD%/../../../Scripts;%PATH%

echo tahcompile tah-*.txt -o output.txt
tahcompile tah-*.txt -o output.txt

pause
