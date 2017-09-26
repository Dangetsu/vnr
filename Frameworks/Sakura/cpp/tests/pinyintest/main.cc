// main.cc
// 1/7/2014 jichi
#include "pinyinconv/pinyinconv.h"
#include <QtCore>
//#include <boost/algorithm/string.hpp>

int main()
{
  qDebug() << "enter";

  const wchar_t *path = L"/Users/jichi/opt/stream/Library/Dictionaries/pinyin/Mandarin.dat";
  //std::wstring s = L"你好";
  std::wstring s = L"女";

  PinyinConverter conv;
  bool ok = conv.addFile(path);
  qDebug() << ok;
  qDebug() << conv.size();

  std::wstring t = conv.convert(s);
  qDebug() << "input:" << QString::fromStdWString(s);
  qDebug() << t.size();
  qDebug() << "output:" << QString::fromStdWString(t);

  qDebug() << "leave";
  return 0;
}

// EOF
