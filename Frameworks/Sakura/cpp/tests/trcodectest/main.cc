// main.cc
// 9/20/2014 jichi
#include "trcodec/trcodec.h"
#include <QtCore>

int main()
{
  qDebug() << "enter";

  //wchar_t ws[] = L"【爽】「悠真女学園くんを攻略すれば２１０円か。なるほどなぁ…」";
  wchar_t ws[] = L"【爽】「悠真くんを攻略すれば２１０円か。なるほどなぁ…」";
  //wchar_t ws[] = L"hello";
  std::wstring text = ws;

  std::wstring path;
  path = L"/Users/jichi/opt/stream/Library/Frameworks/Sakura/cpp/libs/trcodec/example.txt";
  //path = L"/Users/jichi/opt/stream/Caches/tmp/reader/dict/ja-zhs/trans.txt";

  TranslationCoder m;
  m.loadScript(path);
  qDebug() << m.size();

  if (!m.isEmpty()) {
    qDebug() << QString::fromStdWString(text);
    text = m.encode(text);
    qDebug() << QString::fromStdWString(text);

    text = m.decode(text);
    qDebug() << QString::fromStdWString(text);
  }

  qDebug() << "leave";
  return 0;
}

// EOF
