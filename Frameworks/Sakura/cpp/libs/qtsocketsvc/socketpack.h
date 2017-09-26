#ifndef _SOCKETSVC_SOCKETPACK_H
#define _SOCKETSVC_SOCKETPACK_H

// socketpack.h
// 4/29/2014 jichi
//
// This class must be consistent with socketsvc/socketpack.py
#include "qtsocketsvc/socketdef.h"
#include <QtCore/QStringList>

//QTSS_BEGIN_NAMESPACE

namespace SocketService {

// Numbers

enum { // number of bytes of an int32 number
  Int32Size = 4,
  UInt32Size = Int32Size
};
enum { PacketHeadSize = UInt32Size };

inline QByteArray packUInt32(quint32 value)
{
  enum { size = UInt32Size };
  quint8 bytes[size] = {
    static_cast<quint8>( value >> 24),
    static_cast<quint8>((value >> 16) & 0xff),
    static_cast<quint8>((value >> 8)  & 0xff),
    static_cast<quint8>( value        & 0xff)
  };
  return QByteArray(reinterpret_cast<char *>(bytes), size);
}

inline quint32 unpackUInt32(const QByteArray &data, int offset = 0)
{
  // QByteArray by default is an array of char, which is signed char. quint8 is unsigned.
  const quint8 *p = reinterpret_cast<const quint8 *>(data.constData()); // signed to unsigned
  return data.size() < 4 ? 0 :
        (static_cast<quint32>(p[offset])     << 24)
      | (static_cast<quint32>(p[offset + 1]) << 16)
      | (static_cast<quint32>(p[offset + 2]) <<  8)
      |  static_cast<quint32>(p[offset + 3]);
}

// Raw data

inline QByteArray packPacket(const QByteArray &data)
{ return packUInt32(data.size()) + data; }

inline QByteArray unpackPacket(const QByteArray &data)
{ return data.mid(PacketHeadSize); }

// StingList

// Force using utf8 encoding
QByteArray packStringList(const QStringList &l, const char *encoding = SOCKET_SERVICE_ENCODING);
QStringList unpackStringList(const QByteArray &data, const char *encoding = SOCKET_SERVICE_ENCODING);

} // SocketService

//QTSS_END_NAMESPACE

#endif // _SOCKETSVC_SOCKETPACK_H
