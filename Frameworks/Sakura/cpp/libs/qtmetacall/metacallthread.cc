// metacallthread.cc
// 4/27/2014 jichi
#include "qtmetacall/metacallthread.h"
#include "qtmetacall/metacallthread_p.h"
#include "qtmetacall/metacallpropagator.h"
#include "qtmetacall/metacallobserver.h"
#include <QtCore/QEventLoop>

#define DEBUG "metacallthread"
#include "sakurakit/skdebug.h"

/** Private class */

MetaCallThreadPrivate::MetaCallThreadPrivate(QObject *parent)
  : Base(parent), propagator(nullptr), role(ClientRole), port(0)
{}

void MetaCallThreadPrivate::connectPropagator()
{
  if (propagator)
    connect(this, SIGNAL(stopRequested()), propagator, SLOT(stop()), Qt::QueuedConnection);
}

void MetaCallThreadPrivate::disconnectPropagator()
{
  if (propagator)
    disconnect(propagator);
}

/** Public class */

// - Construction -

MetaCallThread::MetaCallThread(QObject *parent)
  : Base(parent), d_(new D(this)) {}

MetaCallThread::~MetaCallThread() { delete d_; }

MetaCallPropagator *MetaCallThread::propagator() const
{ return d_->propagator; }

void MetaCallThread::setPropagator(MetaCallPropagator *value)
{
  if (d_->propagator != value) {
    if (d_->propagator)
      d_->disconnectPropagator();
    d_->propagator = value;
    if (value) {
      if (!value->socketObserver())
        value->setSocketObserver(new MetaCallSocketObserver(value));
      d_->connectPropagator();
    }
  }
}

// - Run -

void MetaCallThread::startClient(const QString &address, int port)
{
  d_->role = D::ClientRole;
  d_->address = address;
  d_->port = port;
  start();
}

void MetaCallThread::startServer(const QString &address, int port)
{
  d_->role = D::ServerRole;
  d_->address = address;
  d_->port = port;
  start();
}

void MetaCallThread::run()
{
  if (d_->propagator)
    switch (d_->role) {
    case D::ClientRole: d_->propagator->startClient(d_->address, d_->port); break;
    case D::ServerRole: d_->propagator->startServer(d_->address, d_->port); break;
    }
  exec();
}

void MetaCallThread::stop() { d_->emit stopRequested(); }

void MetaCallThread::waitForReady() const
{
  if (d_->propagator && !d_->propagator->isReady())
    if (MetaCallSocketObserver *s = d_->propagator->socketObserver()) {
      QEventLoop loop;
      connect(s, SIGNAL(connected()), &loop, SLOT(quit()));
      connect(s, SIGNAL(disconnected()), &loop, SLOT(quit()));
      connect(s, SIGNAL(error()), &loop, SLOT(quit()));
      loop.exec();
      //do loop.exec();
      //while (!d_->propagator->isReady());
    }
}

// - Actions -

// EOF
