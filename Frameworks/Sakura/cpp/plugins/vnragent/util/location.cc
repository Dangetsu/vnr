// location.cc
// 5/3/2014 jichi
//
// As QDesktopServices is in QtGui, calculate locations myself.
#include "util/location.h"
#include <windows.h>
#include <shlobj.h>
#include <QtCore/QFileInfo>

namespace { // unnamed

QString getDesktopLocation()
{
  // Manually get desktop location since QtGui does not exist
  // http://stackoverflow.com/questions/17933917/get-the-users-desktop-folder-using-windows-api
  wchar_t buf[MAX_PATH];
  if (S_OK == ::SHGetFolderPathW(nullptr, CSIDL_DESKTOPDIRECTORY, nullptr, 0, buf))
    return QString::fromWCharArray(buf);
  return QString();
}

QString getModulePath(const char *name)
{
  wchar_t path[MAX_PATH];
  if (HMODULE hModule = ::GetModuleHandleA(name))
    if (::GetModuleFileNameW(hModule, path, MAX_PATH))
      return QString::fromWCharArray(path);
  return QString();
}

QString dirname(const QString &path)
{ return QFileInfo(path).path(); } // use path instead of filePath in case path is empty

} // unnamed namespace

QString Util::desktopLocation()
{
  static QString ret;
  if (ret.isEmpty())
    ret = ::getDesktopLocation();
  return ret;
}

QString Util::qtLocation()
{
  static QString ret;
  if (ret.isEmpty())
    ret = ::dirname(::getModulePath("QtCore4.dll"));
  return ret;
}

QString Util::qtPrefix() { return ::dirname(qtLocation()); }

QString Util::vnrLocation()
{
  static QString ret;
  if (ret.isEmpty())
    ret =
      ::dirname( // VNR
      ::dirname( // VNR/Library
      ::dirname( // VNR/Library/Frameworks
      ::dirname( // VNR/Library/Frameworks/Qt
      ::dirname( // VNR/Library/Frameworks/Qt/PySide
      ::getModulePath("QtCore4.dll") // VNR/Library/Frameworks/Qt/PySide/QtCore4.dll
    )))));
  return ret;
}

// EOF
