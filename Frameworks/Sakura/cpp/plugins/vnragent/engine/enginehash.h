#pragma once

// enginehash.h
// 4/26/2014 jichi
// Hashing algorithms are so important that I put them into a different file.

#include "sakurakit/skhash.h"
#include <QtCore/QString>

#ifdef _MSC_VER
# pragma warning (disable:4334)   // C4334: 32-bit shift implicit converted to 64 bits
#endif // _MSC_VER

namespace Engine {

// Cast quint64 to qint64

inline qint64 hashByteArray(const QByteArray &b, qint64 h = Sk::djb2_hash0)
{ return Sk::djb2_n(reinterpret_cast<const quint8 *>(b.constData()), b.size(), h); }

inline qint64 hashString(const QString &s, qint64 h = Sk::djb2_hash0)
{ return Sk::djb2_n(reinterpret_cast<const quint8 *>(s.utf16()), s.size() * 2, h); }

inline qint64 hashCharArray(const void *lp)
{ return Sk::djb2(reinterpret_cast<const quint8 *>(lp)); }

inline qint64 hashCharArray(const void *lp, size_t len, qint64 h = Sk::djb2_hash0)
{ return Sk::djb2_n(reinterpret_cast<const quint8 *>(lp), len, h); }

inline qint64 hashWCharArray(const wchar_t *lp, size_t len = -1, qint64 h = Sk::djb2_hash0)
{
  if (len == -1)
    len = ::wcslen(lp);
  return Sk::djb2_n(reinterpret_cast<const quint8 *>(lp), 2 * len, h);
}

inline qint64 hashWString(const QString &s, qint64 h = Sk::djb2_hash0)
{ return hashWCharArray(s.utf16(), s.size(), h); }

inline qint64 hashTextKey(qint64 hash, unsigned role) { return hash + (1 << role); }

// This is consistent with textthread_p in texthook
//inline qint32 hashThreadSignature(ulong returnAddress, ulong split = 0)
//{
//  return (returnAddress & 0xffff)  // context
//       | (split & 0xffff) << 16;   // subcontext
//}
inline qint32 hashThreadSignature(ulong role, ulong split = 1)
{
  return (split & 0xffff) // context
       | (role << 16);    // subcontext
}

} // namespace Engine

// EOF
