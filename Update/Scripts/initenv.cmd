:: coding: sjis, ff=dos
:: 11/12/2012 jichi

::set CYGWIN=nodosfilewarning

:: http://docs.python.org/2/using/cmdline.html#envvar-PYTHONDONTWRITEBYTECODE
set PYTHONDONTWRITEBYTECODE=1

set PATH=%~dp0/../GnuWin32;%PATH%
set PATH=%~dp0/../7z;%PATH%
::set PATH=%~dp0/../Mercurial;%PATH%
set PATH=%~dp0/../../Frameworks/Python;%PATH%
set PATH=%~dp0/../../Frameworks/Python/Scripts;%PATH%

set REPO_IP=153.121.52.138
set REPO_HOST=sakuradite.org

set HG_OPT=-v --debug
set HG=call hg %HG_OPT%

:: EOF
