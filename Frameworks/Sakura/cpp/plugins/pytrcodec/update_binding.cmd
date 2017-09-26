:: update_binding.cmd
:: 10/6/2012 jichi
:: See: http://qt-project.org/wiki/Category:LanguageBindings::PySide::Shiboken::PySide_Binding_Generation_Tutorial
:: See: http://blog.csdn.net/dbzhang800/article/details/6387577
@setlocal
cd /d "%~dp0"
set TARGET=trcodec
set LIBTARGET=%TARGET%
set PYTARGET=py%TARGET%
set HEADER=%PYTARGET%_config.h
set TYPESYSTEM=typesystem_%TARGET%.xml
set OUTDIR=binding
set DESTDIR=%CD%/../../../bin
set LOG=%OUTDIR%.log
rm -Rf "%OUTDIR%".bak
if exist "%OUTDIR%" ren "%OUTDIR%" "%OUTDIR%".bak
rm -Rf %OUTDIR% %LOG%

set LIBPATH=%CD%/../../libs
set TYPESYSTEM_HOME=%CD%/../../typesystems
set TYPESYSTEM_PATH=%TYPESYSTEM_HOME%/cpp;%TYPESYSTEM_HOME%/stl

set TARGET_HOME=../../libs/%LIBTARGET%
set QT_HOME=c:/qt/4
::set PYTHON_HOME=%CD%/../../../../Python
::set PYTHON_HOME=c:/python27
set PYTHON_HOME=z:/Local/Windows/Developer/Python
set PYSIDE_HOME=%PYTHON_HOME%/Lib/site-packages/PySide

set PATH=%QT_HOME%/bin;%PYSIDE_HOME%;%PATH%

::
:: Essential:
:: --avoid-protected-hack           Otherwise link time error for Qt
:: --enable-pyside-extensions       Enable Slot/Signal
::
:: Suggested by Qt wiki:
:: --enable-parent-ctor-heuristic   Detect parent ctor
:: --use-isnull-as-nb_nonzero       Use isNull for comparison
:: --enable-return-value-heuristic  Detect ownership in return value
::
set INC=
set INC=%INC%;%QT_HOME%/include
set INC=%INC%;%QT_HOME%/include/Qt
set INC=%INC%;%QT_HOME%/include/QtCore
set INC=%INC%;%PYTHON_HOME%/include
set INC=%INC%;%PYSIDE_HOME%/include
set INC=%INC%;%PYSIDE_HOME%/include/shiboken
set INC=%INC%;%PYSIDE_HOME%/include/PySide
set INC=%INC%;%PYSIDE_HOME%/include/PySide/QtCore
set INC=%INC%;%TARGET_HOME%;%LIBPATH%
set INC=%INC%;..

set _=
::set _= %_% --debug-level=full --no-suppress-warnings
:: Disable Qt
::set _=%_% --enable-pyside-extensions
set _=%_% --enable-parent-ctor-heuristic
set _=%_% --use-isnull-as-nb_nonzero
set _=%_% --enable-return-value-heuristic
set _=%_% --avoid-protected-hack
set _=%_% --include-paths=%INC%
set _=%_% --typesystem-paths=%PYSIDE_HOME%/typesystems;%TYPESYSTEM_PATH%
set _=%_% --output-directory=%OUTDIR%

>"%LOG%" shiboken %HEADER% %TYPESYSTEM% %_% || exit /b 1
dos2unix %OUTDIR%/* %OUTDIR%/*/*
head "%LOG%"
tail "%LOG%"

:: EOF

::set INCLUDE=%PYSIDE_HOME%/include/shiboken;%PYTHON_HOME%/include;%INCLUDE%
::set INCLUDE=%PYSIDE_HOME%/include;%PYSIDE_HOME%/include/PySide;%PYSIDE_HOME%/include/PySide/QtCore;%PYSIDE_HOME%/include/PySide/QtGui;%INCLUDE%
::set INCLUDE=%INC%;%INCLUDE%
::set LIB=%PYTHON_HOME%/libs;%PYSIDE_HOME%;%LIB%
::set LIB=%QT_HOME%/lib;%LIB%
::set LIB=%DESTDIR%;%LIB%
::set _=
::set _=%_% -EHsc -LD -DUNICODE
::set _=%_% python27.lib shiboken-python2.7.lib pyside-python2.7.lib
::set _=%_% QtCore4.lib QtGui4.lib
::set _=%_% %DESTDIR%/%TARGET%.lib
::set _=%_% /I.
::set _=%_% /I%OUTDIR%/%TARGET%
::set PREFIX=%OUTDIR%/%TARGET%/%TARGET%
::cl %_% %PREFIX%_module_wrapper.cpp %PREFIX%_wrapper.cpp /Fe%TARGET%.pyd
