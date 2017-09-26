// main.cc
// 4/25/2014 jichi

#include <QtCore/QHash>
#include <QtCore/QDebug>

int main(int argc, char *argv[])
{
  if (argc > 1)
    for (int i = 1; i < argc; i++)
      qDebug() << qHash(QString::fromLocal8Bit(argv[i]));
  //qDebug() << qHash("ping");
  return 0;
}
