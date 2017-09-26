// main.cc
// 9/5/2014 jichi
// http://stackoverflow.com/questions/940707/how-do-i-programatically-get-the-version-of-a-dll-or-exe-file
#include "winversion/winversion.h"
#include <qt_windows.h>
#include <QtCore>

int main()
{
  WCHAR path[] = L"C:\\Applications\\ppsspp-0.9.9.1\\PPSSPPWindows.exe";
  //const wchar_t *path = L"C:\\Windows\\notepad.exe";
  int ver[4];
  WinVersion::queryFileVersion(path, ver);
  //queryFileInfo(path, &ver);
  qDebug() << ver[0] << ver[1] << ver[2] << ver[3];
  return 0;
}

// EOF
