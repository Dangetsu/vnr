// main.cc
// 4/21/2014 jichi

#include "qtjson/qtjson.h"
#include <QtGui>

int main(int argc, char *argv[])
{
  QApplication a(argc, argv);

  QHash<QString, QVariant> x;
  x["hello"] = QString::fromWCharArray(L"\"");

  QString t = QtJson::stringify(x);

  auto w = new QTextEdit;
  w->setPlainText(t);

  w->resize(400, 300);
  w->show();
  return a.exec();
}
