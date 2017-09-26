// main.cc
// 9/20/2014 jichi
#include "simplecc/simplecc.h"
#include <QtCore>

int main()
{
  qDebug() << "enter";

  //wchar_t ws[] = L"風";
  wchar_t ws[] = L"轻轻地";
  //wchar_t ws[] = L"说什么";
  //QString text = QString::fromWCharArray(ws);
  std::wstring text = ws;

  std::wstring path;
  //path = L"../cpp/libs/trscript/example.txt";
  //path = L"/Users/jichi/stream/Library/Dictionaries/opencc/JPVariants.txt";
  path = L"/Users/jichi/stream/Library/Dictionaries/opencc/TSCharacters.txt";
  //path = L"../../../../Caches/tmp/reader/dict/zhs/test.txt";

  SimpleChineseConverter conv;
  conv.addFile(path, true);
  qDebug() << conv.size();

  if (!conv.isEmpty()) {
    qDebug() << QString::fromStdWString(text);
    std::wstring result = conv.convert(text);
    qDebug() << QString::fromStdWString(result);
    qDebug() << (text == result);
    qDebug() << conv.needsConvert(text);
    qDebug() << conv.needsConvert(result);
  }

  qDebug() << "leave";
  return 0;
}

// EOF
