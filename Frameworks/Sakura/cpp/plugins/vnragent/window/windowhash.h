#pragma once

// windowhash.h
// 2/1/2013 jichi
// Hashing algorithms are so important that I put them into a different file.

#include "sakurakit/skhash.h"
#include <QtCore/QString>
#include <QtGui/qwindowdefs.h>

namespace Window {

// Cast quint64 to qint64

inline qint64 hashByteArray(const QByteArray &b)
{ return Sk::djb2_n(reinterpret_cast<const quint8 *>(b.constData()), b.size()); }

inline qint64 hashString(const QString &s)
{ return Sk::djb2_n(reinterpret_cast<const quint8 *>(s.utf16()), s.size() * 2); }

inline qint64 hashCharArray(const void *lp, size_t len)
{ return Sk::djb2_n(reinterpret_cast<const quint8 *>(lp), len); }

inline qint64 hashWCharArray(const wchar_t *lp, size_t len)
{ return Sk::djb2_n(reinterpret_cast<const quint8 *>(lp), 2 * len); }

enum TextRole {
  WindowTextRole = 0
  , MenuTextRole = 1 << 16
  , ListTextRole = 2 << 16
  , TabTextRole = 3 << 16
};

inline long hashWindow(WId window)
{ return reinterpret_cast<long>(window); }

inline long hashWindowItem(WId window, uint role, size_t index = 0)
{ return reinterpret_cast<long>(window) + index + role; }

//inline bool isTranslatedText(const QString &t)
//{ return t.contains('<') && !t.contains('>'); }

} // namespace Window

// EOF
