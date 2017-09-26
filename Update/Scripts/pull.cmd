:: coding: sjis, ff=dos
:: 12/17/2012 jichi
@echo off
setlocal
cd /d %~dp0
cd ../..
set PATH=%CD%/Frameworks/Python/Scripts
set HG_OPT=-v --debug
set HG=hg
::set HG=call hg

if not exist .hgignore exit /b 1

for %%i in (
    . ^
    Frameworks\Python ^
    Frameworks\EB ^
    Frameworks\Sakura ^
  ) do (
  if exist %%i (
    pushd %%i
    echo hg pullup: %%i
    %HG% %HG_OPT% pull && hg up
    popd
  )
)

:: EOF
