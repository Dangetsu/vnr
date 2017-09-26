// metacallpropagator.cc
// 4/9/2012 jichi
#include "qtmetacall/metacallpropagator.h"
#include "qtmetacall/metacallpropagator_p.h"
#include "qtmetacall/metacallobserver.h"
#include "qtmetacall/metacallfilter_p.h"
#include <QtCore/QEventLoop>
#include <QtNetwork/QHostAddress>
#include <QtNetwork/QTcpServer>
#include <QtNetwork/QTcpSocket>

#ifdef __clang__
# pragma GCC diagnostic ignored "-Wlogical-op-parentheses"
#endif // __clang__

#define DEBUG "metacallpropagator"
#include "sakurakit/skdebug.h"

/** Private class */

MetaCallPropagatorPrivate::MetaCallPropagatorPrivate(QObject *parent)
  : Base(parent), filter(nullptr), socketObserver(nullptr), server(nullptr), socket(nullptr)
{}

void MetaCallPropagatorPrivate::dumpSocketInfo() const
{
  if (socket)
    DOUT("socket"
         ": localAddress ="<< socket->localAddress() <<
         ", localPort ="   << socket->localPort() <<
         ", peerAddress =" << socket->peerAddress() <<
         ", peerPort ="    << socket->peerPort() <<
         ", state ="       << socket->state() <<
         ", error ="       << socket->errorString());
  else
    DOUT("socket = null");
}

void MetaCallPropagatorPrivate::createFilter(QObject *watched)
{
  Q_ASSERT(watched);
  filter = new MetaCallSocketFilter(this);
  filter->setWatchedObject(watched);
  watched->installEventFilter(filter);
}

// FIXME: According to this structure, it can only accept one client at a time
// The client has to reconnect on error.
void MetaCallPropagatorPrivate::serverAcceptsConnection()
{
  DOUT("enter");
  if (socket) {
    if (socket->isOpen())
      socket->close();
    socket->deleteLater();
  }
  if (server)
    socket = server->nextPendingConnection();
  else
    socket = nullptr;
  if (filter)
    filter->setSocket(socket);
  //dumpSocketInfo();
  if (socket) {
#ifdef DEBUG
    connect(socket, SIGNAL(error(QAbstractSocket::SocketError)), SLOT(dumpSocketInfo()));
    connect(socket, SIGNAL(stateChanged(QAbstractSocket::SocketState)), SLOT(dumpSocketInfo()));
#endif // DEBUG
    connectSocketObserver();
  }
  DOUT("leave: ok =" << bool(socket));
}

void MetaCallPropagatorPrivate::connectSocketObserver()
{
  if (socket && socketObserver) {
    connect(socket, SIGNAL(connected()), socketObserver, SIGNAL(connected()));
    connect(socket, SIGNAL(disconnected()), socketObserver, SIGNAL(disconnected()));
    connect(socket, SIGNAL(error(QAbstractSocket::SocketError)), socketObserver, SIGNAL(error()));
  }
}

void MetaCallPropagatorPrivate::disconnectSocketObserver()
{
  if (socket && socketObserver)
    socket->disconnect(socketObserver);
    //disconnect(socket, SIGNAL(connected()), socketObserver, SIGNAL(connected()));
    //disconnect(socket, SIGNAL(disconnected()), socketObserver, SIGNAL(disconnected()));
    //disconnect(socket, SIGNAL(error(QAbstractSocket::SocketError)), socketObserver, SIGNAL(error()));
}


/** Public class */

// - Construction -

MetaCallPropagator::MetaCallPropagator(QObject *parent)
  : Base(parent), d_(new D(this)) {}

MetaCallPropagator::~MetaCallPropagator()
{
  stop();
  delete d_;
}

bool MetaCallPropagator::isServer() const // thread-safe
{ return d_->server; }

bool MetaCallPropagator::isClient() const // thread-safe
{ return !d_->server && d_->socket; }

MetaCallRouter *MetaCallPropagator::router() const
{ return d_->filter ? d_->filter->router() : nullptr; }

void MetaCallPropagator::setRouter(MetaCallRouter *value)
{
  if (!d_->filter)
    d_->createFilter(this);
  d_->filter->setRouter(value);
}

MetaCallSocketObserver *MetaCallPropagator::socketObserver() const
{ return d_->socketObserver; }

void MetaCallPropagator::setSocketObserver(MetaCallSocketObserver *value)
{
  if (d_->socketObserver != value) {
    if (d_->socketObserver)
      d_->disconnectSocketObserver();
    d_->socketObserver = value;
    if (value && d_->socket)
      d_->connectSocketObserver();
  }
}

// - Service -

bool MetaCallPropagator::isActive() const // thread-safe
{
  if (auto p = d_->server)
    return p->isListening();
  if (auto p = d_->socket)
    return p->state() == QAbstractSocket::ConnectedState;
  return false;
}

bool MetaCallPropagator::isReady() const // thread-safe
{
  if (auto p = d_->socket) {
    auto s = p->state();
    return s == QAbstractSocket::ConnectedState || s == QAbstractSocket::UnconnectedState;
  }
  return false;
}

void MetaCallPropagator::waitForReady() const
{
  if (d_->socket &&
      d_->socket->state() != QAbstractSocket::ConnectedState &&
      d_->socket->state() != QAbstractSocket::UnconnectedState) {
    QEventLoop loop;
    connect(d_->socket, SIGNAL(stateChanged(QAbstractSocket::SocketState)), &loop, SLOT(quit()));
    connect(d_->socket, SIGNAL(error(QAbstractSocket::SocketError)), &loop, SLOT(quit()));
    do loop.exec();
    while (!d_->socket ||
           d_->socket->state() == QAbstractSocket::HostLookupState ||
           d_->socket->state() == QAbstractSocket::ConnectingState);
  }
}

bool MetaCallPropagator::startServer(const QString &address, int port)
{
  DOUT("enter: address =" << address << ", port =" << port);
  if (d_->server) {
    DOUT("leave: ret = false, already started");
    return false;
  }

  d_->server = new QTcpServer(this);
  bool ok = d_->server->listen(QHostAddress(address), port);
  if (ok) {
    DOUT("server.connect: address =" << d_->server->serverAddress() << ", port =" << d_->server->serverPort());
    connect(d_->server, SIGNAL(newConnection()), d_, SLOT(serverAcceptsConnection()));
  } else {
    DOUT("error =" << d_->server->errorString());
    stop();
  }
  if (ok && !d_->filter)
    d_->createFilter(this);
  DOUT("leave: ret =" << ok);
  return ok;
}

bool MetaCallPropagator::startClient(const QString &address, int port)
{
  DOUT("enter: address =" << address << ", port =" << port);
  if (d_->socket) {
    DOUT("leave: ret = false, already started");
    return false;
  }

  d_->socket = new QTcpSocket(this);
#ifdef DEBUG
  connect(d_->socket, SIGNAL(error(QAbstractSocket::SocketError)), d_, SLOT(dumpSocketInfo()));
  connect(d_->socket, SIGNAL(stateChanged(QAbstractSocket::SocketState)), d_, SLOT(dumpSocketInfo()));
#endif // DEBUG
  d_->socket->connectToHost(QHostAddress(address), port);

  if (!d_->filter)
    d_->createFilter(this);
  d_->filter->setSocket(d_->socket);

  d_->connectSocketObserver();

  DOUT("leave: ret = true");
  return true;
}

void MetaCallPropagator::stop()
{
  if (d_->filter)
    d_->filter->setSocket(nullptr);
  if (d_->socket) {
    if (d_->socket->isOpen())
      d_->socket->close();
    if (!d_->server)
      d_->socket->deleteLater();
    d_->socket = nullptr;
  }
  if (d_->server) {
    if (d_->server->isListening())
      d_->server->close();
    d_->server->deleteLater();
    d_->server = nullptr;
  }
}

// EOF
