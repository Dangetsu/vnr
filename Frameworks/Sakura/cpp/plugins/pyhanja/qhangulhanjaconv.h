#ifndef QHANGULHANJACONV_H
#define QHANGULHANJACONV_H

// qhangulhanjaconv.h
// 1/6/2015 jichi
// Qt is used instead of pure C++ to reduce memory copy of the returned containers.

#include "sakurakit/skglobal.h"
#include <QtCore/QList>
#include <QtCore/QPair>
#include <QtCore/QString>

class QHangulHanjaConverter_p;
class QHangulHanjaConverter
{
  SK_CLASS(QHangulHanjaConverter)
  SK_DISABLE_COPY(QHangulHanjaConverter)
  SK_DECLARE_PRIVATE(QHangulHanjaConverter_p)

public:
  // Construction
  QHangulHanjaConverter();
  ~QHangulHanjaConverter();

  ///  Return the number of loaded rules
  int size() const;

  ///  Return whether the script has been loaded, thread-safe
  bool isEmpty() const;

  ///  Clear the loaded script
  void clear();

  ///  Add script from file
  bool loadFile(const QString &path);

  // Parse

  // Replace the characters according to the script, thread-safe
  QString convert(const QString &text) const;

  // Replace the characters according to the script, thread-safe
  QList<QList<QPair<QString, QString> > > parse(const QString &text) const;
};

#endif // QHANGULHANJACONV_H
