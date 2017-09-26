// metacallfilter_p.cc
// 4/9/2012 jichi
#include "qtmetacall/metacallfilter_p.h"
#include "qtmetacall/metacallrouter.h"
#include "qtmetacall/qmetacallevent_p.h"
#include <QtCore/QEvent>
#include <QtNetwork/QAbstractSocket>
#include <memory> // for unique_ptr
//#include "../../plugins/vnragent/growl.h"

#define DEBUG "metacallfilter"
#include "sakurakit/skdebug.h"

#ifdef __GNUC__
# pragma GCC diagnostic ignored "-Wparentheses" // suggest parentheses
#endif // __GNUC__

#ifdef Q_OS_MAC
# define unique_ptr  auto_ptr  // TR1 requires libc++
#endif // Q_OS_MAC

/** Private class */

class MetaCallSocketFilterPrivate
{
public:
  typedef quint16 message_size_t;
  message_size_t messageSize;
  QAbstractSocket *socket;
  QObject *watched; // watched object
  MetaCallRouter *router;

  MetaCallSocketFilterPrivate()
    : messageSize(0), socket(nullptr), watched(nullptr), router(nullptr) {}
};

/** Public class */

// - Construction -

MetaCallSocketFilter::MetaCallSocketFilter(QObject *parent)
  : Base(parent), d_(new D) {}

MetaCallSocketFilter::~MetaCallSocketFilter()
{ delete d_; }

void MetaCallSocketFilter::setSocket(QAbstractSocket *socket)
{
  if (Q_LIKELY(d_->socket != socket)) {
    d_->socket = socket;
    if (socket)
      connect(socket, SIGNAL(readyRead()), SLOT(readSocket()));
  }
}

void MetaCallSocketFilter::setRouter(MetaCallRouter *value)
{ d_->router = value; }

MetaCallRouter *MetaCallSocketFilter::router() const
{ return d_->router; }

void MetaCallSocketFilter::setWatchedObject(QObject *obj)
{ d_->watched = obj; }

bool MetaCallSocketFilter::isActive() const
{ return d_->socket && d_->socket->state() == QAbstractSocket::ConnectedState; }

// - Communication -

bool MetaCallSocketFilter::eventFilter(QObject *watched, QEvent *e)
{
  if (watched == d_->watched && e->type() ==  QEvent::MetaCall && isActive()) {
    DOUT("filtered");
    writeSocket(static_cast<QMetaCallEvent *>(e));
    return true;
  }
  return Base::eventFilter(watched, e);
}

void MetaCallSocketFilter::writeSocket(const QMetaCallEvent *e)
{
  Q_ASSERT(e);
  if (!isActive())
    return;
  DOUT("enter");

  QByteArray message;
  QDataStream out(&message, QIODevice::WriteOnly);

  int m_nargs = e->nargs();
  DOUT("m_nargs =" << m_nargs);

  int m_id = e->id();
  DOUT("m_id =" << m_id);
  if (d_->router) {
    m_id = d_->router->convertSendMethodId(m_id);
    DOUT("writeSocket: convert method id: new id =" << m_id);
  }

  out << D::message_size_t(0) // space holder for message size
      << m_id
      << m_nargs;

  bool ok = true;
  for (int i = 1; i < e->nargs() && ok; i++) {
    out << e->types()[i];
    ok = QMetaType::save(out, e->types()[i], e->args()[i]);
    if (Q_UNLIKELY(!ok))
      DOUT("warning: unregisted metatype");
  }

  if (Q_LIKELY(ok)) {
    out.device()->seek(0);
    out << D::message_size_t(message.size());
    bool ok = d_->socket->write(message) == message.size();
    if (ok)
      d_->socket->waitForBytesWritten();
  }
  DOUT("leave: ok =" << ok);
}

void MetaCallSocketFilter::readSocket()
{
  if (!isActive())
    return;
  DOUT("enter");

  while (qint64 bytesAvailable = d_->socket->bytesAvailable()) {
    // Save messageSize_ since none-blocking read is used
    if (!d_->messageSize && bytesAvailable < int(sizeof(D::message_size_t))) {
      DOUT("leave: insufficient messageSize");
      return;
    }

    QDataStream in(d_->socket);
    if (!d_->messageSize) {
      in >> d_->messageSize;
      bytesAvailable -= sizeof(D::message_size_t);
    }

    if (bytesAvailable < int(d_->messageSize - sizeof(D::message_size_t))) {
      DOUT("leave: insufficient messageSize");
      return;
    }
    DOUT("messageSize =" << d_->messageSize);

    d_->messageSize = 0;

    int m_id;
    in >> m_id;
    DOUT("m_id =" << m_id);

    int m_nargs;
    in >> m_nargs;
    DOUT("m_nargs =" << m_nargs);
    Q_ASSERT(m_nargs > 0);
    if (m_nargs <= 0) {
      DOUT("leave: error, invalid m_nargs =" << m_nargs);
      return;
    }

    int *m_types = new int[m_nargs];
    std::unique_ptr<int> autorelease_types(m_types);

    void **m_args = new void *[m_nargs];
    std::unique_ptr<void *> autorelease_args(m_args);
    m_args[0] = 0;

    bool ok = true;
    for (int i = 1; i < m_nargs && ok; i++) {
      in >> m_types[i];
      m_args[i] = QMetaType::construct(m_types[i]);

      ok = QMetaType::load(in, m_types[i], m_args[i]) && ok;
    }
    if (Q_UNLIKELY(!ok))
      DOUT("warning: unregisted metatype");

    if (ok && d_->watched) {
      if (d_->router) {
        m_id = d_->router->convertReceiveMethodId(m_id);
        DOUT("placeMetaCall: convert method id: new id =" << m_id);
      }
      // See: QObject::event and QQMetaCallEvent implementation in in qobject.cpp
      // Use macros is case QT_NO_EXCEPTIONS is defined
      QT_TRY {
        DOUT("placeMetaCall: method id =" << m_id << ", nargs =" << m_nargs);
        QMetaObject::metacall(d_->watched, QMetaObject::InvokeMetaMethod, m_id, m_args);
      } QT_CATCH(...) {
        DOUT("exception ignored, destroy meta types");
        for (int i = 0; i < m_nargs; i++)
          if (m_types[i] && m_args[i])
            QMetaType::destroy(m_types[i], m_args[i]);
        // Ignore exception
        //QT_RETHROW;
      }
    }
  }
  DOUT("leave: ok = yes");
}

// EOF
