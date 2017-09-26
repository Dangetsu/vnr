// main.cc
// 4/5/2014 jichi
#include <QtCore>

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
  QRegExp rx("\\{(.+)/.+\\}", Qt::CaseSensitive);
  rx.setMinimal(true);
  QString t = "123{123/456}awe}";
  t.replace(rx, "\\1");
  qDebug() << t;

  QByteArray c("\0", 1);
  QByteArray b = "hello";
  qDebug() << b.size();
  b.replace("l", c);
  qDebug() << b.size();
  return 0;
}
