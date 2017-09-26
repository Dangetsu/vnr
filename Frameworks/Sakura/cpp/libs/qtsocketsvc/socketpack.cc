// socketpack.cc
// 4/29/2014 jichi
#include "qtsocketsvc/socketpack.h"
#include <QtCore/QTextCodec>

#define DEBUG "socketpack"
#include "sakurakit/skdebug.h"

//QTSS_BEGIN_NAMESPACE

QByteArray SocketService::packStringList(const QStringList &l, const char *encoding)
{
  QByteArray head, body;
  head.append(packUInt32(l.size()));
  QTextCodec *codec = QTextCodec::codecForName(encoding);
  foreach (const auto &s, l) {
    QByteArray data = codec->fromUnicode(s);
    head.append(packUInt32(data.size()));
    body.append(data);
  }

  //return head + body
  return head.append(body);
}

QStringList SocketService::unpackStringList(const QByteArray &data, const char *encoding)
{
  const quint32 dataSize = data.size(); // never modified in this function
  if (dataSize < UInt32Size) {
    DERR("insufficient list size");
    return QStringList();
  }
  quint32 headOffset = 0;
  quint32 count = unpackUInt32(data, headOffset); headOffset += UInt32Size;
  if (Q_UNLIKELY(count == 0)) {
    DERR("empty list");
    return QStringList();
  }

  quint32 bodyOffset = headOffset + count * UInt32Size;
  if (Q_UNLIKELY(bodyOffset > dataSize)) {
    DERR("insufficient head size");
    return QStringList();
  }

  const char *p = data.constData();

  QTextCodec *codec = QTextCodec::codecForName(encoding);
  QStringList ret;
  for (quint32 i = 0; i < count; i++) {
    quint32 size = unpackUInt32(data, headOffset); headOffset += UInt32Size;
    if (size == 0)
      ret.append(QString());
    // size > 0
    else if (Q_UNLIKELY(bodyOffset + size > dataSize)) {
      DERR("insufficient data size");
      return QStringList();
    } else {
      QString s = codec->toUnicode(p + bodyOffset, size); bodyOffset += size;
      ret.append(s);
    }
  }
  return ret;
}

//QTSS_END_NAMESPACE

// EOF

/*
namespace { // unnamed

// Force using UTF-8
QTextCodec *codec_ = QTextCodec::codecForName(STRING_ENCODING);

//inline QString toUnicode(const QByteArray &data) { return codec_->toUnicode(data); }
inline QString toUnicode(const char *data, int len) { return codec_->toUnicode(data, len); }
inline QByteArray fromUnicode(const QString &str) { return codec_->fromUnicode(str); }

#define packString(...)     fromUnicode(__VA_ARGS__)
#define unpackString(...)   toUnicode(__VA_ARGS__)

} // unnamed namespace
*/
