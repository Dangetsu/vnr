:: Remove VNR Profiles.cmd
:: 8/13/2014 jichi
:: Remove VNR's profiles at APPDATA.
@echo off
setlocal

title Remove VNR Profiles

echo ----------------------------------------------------------------------
echo                          Remove VNR Profiles
echo ----------------------------------------------------------------------
echo This script will delete VNR's user profiles as follows:
echo.
echo     %APPDATA%/org.sakuradite.reader
echo     %APPDATA%/org.sakuradite.browser
echo.
echo Local game settings, text settings, voice settings, and caches will be
echo be deleted PERMANENTLY. VNR will recreate everything at next time.
echo.
echo If you only want to reset VNR's Preferences but keep game settings,
echo please manually double-click the following file instead:
echo.
echo         Remove VNR Settings.reg
echo.
echo Do you want to proceed to delete user profiles?
echo.
pause

echo.
echo Are you sure (1/3)?
echo.
pause
echo.
echo Are you sure (2/3)?
echo.
pause
echo.
echo Are you sure (3/3)?
echo.
pause

echo.
echo ----------------------------------------------------------------------
echo                              Processing ...
echo ----------------------------------------------------------------------

echo rd /s "%APPDATA%\org.sakuradite.reader"
if exist "%APPDATA%/org.sakuradite.reader" rd /s "%APPDATA%\org.sakuradite.reader"

echo rd /s "%APPDATA%\org.sakuradite.browser"
if exist "%APPDATA%/org.sakuradite.browser" rd /s "%APPDATA%\org.sakuradite.browser"

echo.
echo ----------------------------------------------------------------------
echo                                  Done!
echo ----------------------------------------------------------------------
echo.
pause

:: EOF
