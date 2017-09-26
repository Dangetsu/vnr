// main.cc
// 2/2/2015 jichi
#include "hanviet/hanvietconv.h"
#include "hanviet/phrasedic.h"
#include "hanviet/worddic.h"
#include <functional>
#include <QtCore>

using namespace std::placeholders; // for _1, _2, etc.

int main()
{
  qDebug() << "enter";

  std::wstring dicdir = L"/Users/jichi/opt/stream/Library/Dictionaries/hanviet/",
               worddic = dicdir + L"ChinesePhienAmWords.txt",
               phrasedic = dicdir + L"VietPhrase.txt";

  std::wstring t;
  //std::wstring s = L"我说你在说什么？顶。我说。麻婆豆腐";
  std::wstring s = L"以及玻璃窗上的店名──『LaSoleil』。";

  HanVietConverter ht;
  ht.addPhraseFile(phrasedic);
  ht.addWordFile(worddic);

  enum : bool { mark = false };

  t = ht.translate(s, mark);
  qDebug() << QString::fromStdWString(t);

  auto trans = std::bind(&HanVietWordDictionary::translate, ht.wordDicionary(), _1);

  t = ht.phraseDicionary()->analyze(s, mark, [](const std::wstring &s, const std::wstring &t) {
    qDebug() << "align:" << QString::fromStdWString(s) << "=>" << QString::fromStdWString(t);
  }, trans);
  qDebug() << QString::fromStdWString(t);

  qDebug() << "leave";
  return 0;
}

// EOF
