// main.cc
// 9/20/2014 jichi
#include "trscript/trscript.h"
#include <QtCore>

int main()
{
  qDebug() << "enter";

  //wchar_t ws[] = L"ルナ様";
  //wchar_t ws[] = L"「ごめんなさい。こう言う時どんな顔すればいいのか分からないの。」【綾波レイ】";
  wchar_t ws[] = L"是不是什么事…";
  //wchar_t ws[] = L"ABCD";
  //QString text = QString::fromWCharArray(ws);
  std::wstring text = ws;

  std::wstring path;
  path = L"/Users/jichi/opt/stream/Library/Frameworks/Sakura/cpp/libs/trscript/example.txt";
  //path = L"/Users/jichi/opt/stream/Caches/tmp/reader/dict/ja-zhs/game.txt";

  TranslationScriptPerformer m;
  m.loadScript(path);
  qDebug() << m.size();

  if (!m.isEmpty()) {
    qDebug() << QString::fromStdWString(text);
    text = m.transform(text, -1, true);
    qDebug() << QString::fromStdWString(text);
  }

  qDebug() << "leave";
  return 0;
}

// EOF
