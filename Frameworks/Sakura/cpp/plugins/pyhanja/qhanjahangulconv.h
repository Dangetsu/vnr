#ifndef QHANJAHANGULCONV_H
#define QHANJAHANGULCONV_H

// qhanjahangulconv.h
// 1/6/2015 jichi
// Qt is used instead of pure C++ to reduce memory copy of the returned containers.

#include "sakurakit/skglobal.h"
#include <QtCore/QString>

class QHanjaHangulConverter_p;
class QHanjaHangulConverter
{
  SK_CLASS(QHanjaHangulConverter)
  SK_DISABLE_COPY(QHanjaHangulConverter)
  SK_DECLARE_PRIVATE(QHanjaHangulConverter_p)

public:
  // Construction
  QHanjaHangulConverter();
  ~QHanjaHangulConverter();

  ///  Return whether the script has been loaded, thread-safe
  bool isEmpty() const;

  ///  Clear the loaded script
  void clear();

  ///  Add script from file
  bool addWordDictionary(const QString &path);
  bool addCharacterDictionary(const QString &path);

  // Parse

  // Replace the characters according to the script, thread-safe
  QString convert(const QString &text) const;
  QString lookup(const QString &text) const;
  int lookupCharacter(int ch) const;
};

#endif // QHANJAHANGULCONV_H
