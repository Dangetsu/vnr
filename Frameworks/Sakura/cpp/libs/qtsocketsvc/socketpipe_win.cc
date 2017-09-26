// socketpipe_win.cc
// 5/13/2014 jichi
#include "qtsocketsvc/socketpipe_win.h"
//#include "qtsocketsvc/socketpack.h"
#include "qtprivate/d/d_qobject.h"
#include <qt/src/network/socket/qlocalsocket_p.h>
#include <QtCore/QTextCodec>

#define DEBUG "socketpipe"
#include "sakurakit/skdebug.h"

// Get handle

HANDLE SocketService::getLocalSocketPipeHandle(const QLocalSocket *socket)
{
  QLocalSocketPrivate *d = QtPrivate::d_q<QLocalSocketPrivate *>(socket);
  return d ? d->handle : nullptr;
}

HANDLE SocketService::findLocalSocketPipeHandle(const QObject *parent)
{
  if (parent)
    if (auto q = parent->findChild<QLocalSocket *>())
      return getLocalSocketPipeHandle(q);
  return nullptr;
}

// Pipe I/O

//bool SocketService::writePipe(pipe_handle_t h, const QByteArray &data, const bool *quit)
//{ return !data.isEmpty() && writePipe(h, data.constData(), data.size(), quit); }
//
//bool SocketService::writePipe(pipe_handle_t h, const QStringList &data, const bool *quit)
//{ return !data.isEmpty() && writePipe(h, packStringList(data, quit)); }

LPOVERLAPPED SocketService::newPipeOverlapped(const char *eventName)
{
  LPOVERLAPPED p = new OVERLAPPED;
  ::memset(p, 0, sizeof(OVERLAPPED));
  p->hEvent = ::CreateEventA(nullptr, TRUE, FALSE, eventName);
  return p;
}

void SocketService::deletePipeOverlapped(LPOVERLAPPED p)
{
  if (p) {
    if (p->hEvent)
      ::CloseHandle(p->hEvent);
    delete p;
  }
}

// See: qt/src/corelib/qwindowspipewrite.cpp
bool SocketService::writePipe(pipe_handle_t h, const void *data, size_t size, LPOVERLAPPED overlap, const bool *quit)
{
  enum { SleepInterval = 200 };

  if (!data || !size)
    return false;

  // LocalSocket is opened with async IO
  bool deleteOverlapLater = !overlap;
  if (!overlap)
    overlap = newPipeOverlapped();
  else
    overlap->Offset = overlap->OffsetHigh = 0;

  ulong totalWritten = 0;
  const char *pData = static_cast<const char *>(data);
  while ((!quit || !*quit) && totalWritten < size) {
    DWORD written = 0;
    if (!::WriteFile(h, pData + totalWritten, size - totalWritten, &written, overlap)) {
      if (::GetLastError() == 0xe8/*NT_STATUS_INVALID_USER_BUFFER*/) {
        // give the os a rest
        ::Sleep(SleepInterval);
        continue;
      }
      break;
    }
    totalWritten += written;
  }
  if (deleteOverlapLater)
    deletePipeOverlapped(overlap);
  return totalWritten == size;
}


// EOF
