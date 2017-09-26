// main.cc
// 4/5/2014 jichi
#include <QtCore>
#include "qtdyncodec/qtdynsjis.h"

bool encodable(const QChar &c, QTextEncoder *encoder)
{
  if (!encoder || c.isNull())
    return false;
  //if (c.unicode() == '?')
  if (c.unicode() <= 127)
    return true;
  return encoder->fromUnicode(&c, 1) != "?";
}

int main()
{
  DynamicShiftJISCodec codec;
  for (int i = 0x85; i < 0x86; i++)
    for (int j = 1; j < 0x2; j++) {
      char data[] = "\x85\x10\x00\x00";
      data[0] = i;
      data[1] = j;
      QString t = QString::fromWCharArray((wchar_t *)data);
      QByteArray d = codec.encode(t);
      QString s = codec.decode(d);
      if (t != s) {
        qWarning() << "failed:" << i <<j;
        qDebug() << "size:" << codec.size() << d.toHex() << d.size() << QString::number(s[0].unicode(), 16) << QString::number(t[0].unicode(), 16);
      }
    }
  QByteArray d = "\x81\xff";
  QString t = codec.decode(d);
  qDebug() << t[0].unicode();
  qDebug() << codec.isFull() << codec.size() ;
  qDebug() << "exit";
  return 0;
}
