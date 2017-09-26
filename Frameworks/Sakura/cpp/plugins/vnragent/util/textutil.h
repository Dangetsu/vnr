#pragma once

// textutil.h
// 5/7/2014 jichi

#include <QtCore/QString>

namespace Util {

///  Assume the text is Japanese, and return if it is not understandable for non-Japanese speakers.
bool needsTranslation(const QString &text);

bool allHangul(const wchar_t *s);

inline bool allHangul(const QString &text)
{ return allHangul(static_cast<const wchar_t *>(text.utf16())); }

inline bool allAscii(const char *s)
{
  while (*s)
    if ((signed char)*s++ < 0)
      return false;
  return true;
}

inline bool allAscii(const wchar_t *s)
{
  while (*s)
    if (*s++ >= 128)
      return false;
  return true;
}

inline bool allAscii(const char *s, size_t size)
{
  for (size_t i = 0; s[i] && i < size; i++)
    if ((signed char)*s++ < 0)
      return false;
  return true;
}

inline bool allAscii(const wchar_t *s, size_t size)
{
  for (size_t i = 0; s[i] && i < size; i++)
    if (*s++ >= 128)
      return false;
  return true;
}

inline bool allAscii(const QString &text)
{ return allAscii(static_cast<const wchar_t *>(text.utf16())); }

inline bool allSpace(const char *s)
{
  while (*s)
    if (!::isspace(*s++))
      return false;
  return true;
}
//inline bool allSpace(const wchar_t *s)
//{
//  while (*s)
//    if (!::iswspace(*s++))
//      return false;
//  return true;
//}
inline bool allSpace(const QString &text)
{
  foreach (const QChar &ch, text)
    if (!ch.isSpace())
      return false;
  return true;
}

//  Return the number of thin characters
inline size_t measureTextSize(const wchar_t *s)
{
  size_t ret = 0;
  while (*s)
    ret += (127 >= *s++) ? 1 : 2;
  return ret;
}

inline size_t measureTextSize(const wchar_t *begin, const wchar_t *end)
{
  size_t ret = 0;
  while (*begin && begin != end)
    ret += (*begin++ <= 127) ? 1 : 2;
  return ret;
}

inline size_t measureTextSize(const QString &text)
{ return measureTextSize(static_cast<const wchar_t *>(text.utf16())); }

QString thin2wide(const QString &text);
QString wide2thin(const QString &text);

} // namespace Util

// EOF
