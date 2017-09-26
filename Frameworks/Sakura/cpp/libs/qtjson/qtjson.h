#ifndef QTJSON_H
#define QTJSON_H

// qtjson.h
// 2/1/2013 jichi

#include <QtCore/QString>

QT_FORWARD_DECLARE_CLASS(QVariant)

namespace QtJson {

///  Return escaped special string if succeed
inline const char *escapeSpecialChar(ushort ch)
{
  switch (ch) {
  case '\\': return "\\\\";
  case '"': return "\\\"";
  case '\n': return "\\n";
  case '\r': return "\\r";
  case '\t': return "\\t";
  case '\b': return "\\b";
  case '\f': return "\\f";
  default: return nullptr;
  }
}

///  Return \uXXXX
inline QString escapeUnicode(ushort ch)
{
  QString r = QString::number(ch, 16);
  while (r.size() < 4)
    r.prepend('0');
  return "\\u" + r;
}

QString stringify(const QVariant &v);

} // namespace QtJson

#endif // QTJSON
