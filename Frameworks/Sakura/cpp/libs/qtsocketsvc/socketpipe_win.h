#ifndef _SOCKETSVC_SOCKETPIPE_WIN_H
#define _SOCKETSVC_SOCKETPIPE_WIN_H

// socketpipe_win.h
// 5/13/2014 jichi

#include <QtCore/QtGlobal>
#ifndef Q_OS_WIN
# error "Windows only"
#endif // Q_OS_WIN

#include <qt_windows.h>

QT_FORWARD_DECLARE_CLASS(QObject)
QT_FORWARD_DECLARE_CLASS(QLocalSocket)

namespace SocketService {

typedef HANDLE pipe_handle_t;

///  Return the named pipe file handle associated with the socket
pipe_handle_t getLocalSocketPipeHandle(const QLocalSocket *socket);

///  Find QLocalSocket and return its named pipe file handle
pipe_handle_t findLocalSocketPipeHandle(const QObject *parent);

///  Blocking writing pipe. quit: indicate whether stop writing.
bool writePipe(pipe_handle_t h, const void *data, size_t size, LPOVERLAPPED overlap = nullptr, const bool *quit = nullptr);
//bool writePipe(pipe_handle_t h, const QByteArray &data, LPOVERLAPPED async = nullptr, const bool *quit = nullptr);
//bool writePipe(pipe_handle_t h, const QStringList &data, LPOVERLAPPED async = nullptr, const bool *quit = nullptr);

///  Create an overlap for pipe with the given event name
LPOVERLAPPED newPipeOverlapped(const char *eventName = nullptr);
void deletePipeOverlapped(LPOVERLAPPED p);

} // SocketService

#endif // _SOCKETSVC_SOCKETPIPE_WIN_H
