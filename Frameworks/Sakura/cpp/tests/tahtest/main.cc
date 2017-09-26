// main.cc
// 8/14/2014 jichi
#include "tahscript/tahscript.h"
#include <QtCore>

int main()
{
  qDebug() << "enter";

  wchar_t ws[] = L"test";
  QString text = QString::fromWCharArray(ws);

  QString path = "../../../Dictionaries/tahscript/atlas.txt";

  TahScriptManager m;
  m.loadFile(path);

  if (!m.isEmpty()) {
    qDebug() << text;
    text = m.translate(text);
    qDebug() << text;
  }

  qDebug() << "leave";
  return 0;
}

// EOF
