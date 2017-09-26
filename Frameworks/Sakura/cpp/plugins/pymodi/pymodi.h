#ifndef PYMODI_H
#define PYMODI_H

// pymodi.h
// 8/13/2014 jichi
//
// Qt is used instead of pure C++ to reduce memory copy of the returned containers.

#include <QtCore/QStringList>

// This class is supposed to be a singleton.
// All methods here are stateless, and supposed to be static.
class ModiReader
{
public:
  ///  Return whether MODI is available
  static bool isValid();

  /**  Read image at path with MODI language and return list of string
   *  @param  path  image path, could be either TIFF or JPEG
   *  @param  language  language enum defined in modi.h
   */
  static QString readText(const QString &path, int language);
  static QStringList readTextList(const QString &path, int language);
};

#endif // PYMODI_H
