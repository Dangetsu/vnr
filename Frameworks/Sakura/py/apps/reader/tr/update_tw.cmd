:: update_tw.cmd
:: 2/17/2013 jichi
@setlocal
@echo off

set zhs2zht=opencc -c s2twp.json -i

call :zhs2zht zh_CN.ts zh_TW.ts

exit /b 0

:zhs2zht input output
  echo %zhs2zht% %1 ^> %2
  call %zhs2zht% %1 | sed "s/zh_CN/zh_TW/g" > %2
  ::opencc -c c:\\dev\\opencc\\bin\\zhs2zht.ini -i %1 -o %2
  dos2unix %2

:: EOF
