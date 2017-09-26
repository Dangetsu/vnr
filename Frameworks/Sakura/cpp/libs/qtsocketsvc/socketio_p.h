#ifndef _SOCKETSVC_SOCKET_P_H
#define _SOCKETSVC_SOCKET_P_H

// socketio_p.h
// 4/29/2014 jichi
//
// This class must be consistent with socketsvc/socketpack.py
#include "qtsocketsvc/socketdef.h"
#include <QtCore/QByteArray>

QT_FORWARD_DECLARE_CLASS(QIODevice)

namespace SocketService {

QString toPipeName(const QString &serverName);

QByteArray readSocket(QIODevice *socket, quint32 &dataSize);
bool writeSocket(QIODevice *socket, const QByteArray &data, bool pack = true);

} // SocketService

//QTSS_END_NAMESPACE

#endif // _SOCKETSVC_SOCKETIO_P_H
