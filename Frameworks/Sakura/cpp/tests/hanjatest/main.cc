// main.cc
// 1/6/2014 jichi
#include "hanjaconv/hangul2hanja.h"
#include "hanjaconv/hanja2hangul.h"
#include <QtCore>

void test_hanja2hangul()
{
  qDebug() << "enter";

  const wchar_t *worddic = L"/Users/jichi/opt/stream/Library/Dictionaries/hanja/dic4.txt",
                *chardic = L"/Users/jichi/opt/stream/Library/Dictionaries/hanja/dic1.txt";
  std::wstring s = L"蓮花蓮";

  HanjaHangulConverter conv;
  conv.addWordDictionary(worddic);
  conv.addCharacterDictionary(chardic);

  conv.replace(&*s.begin());

  qDebug() << QString::fromStdWString(s);

  qDebug() << "leave";
}

void test_hangul2hanja()
{
  qDebug() << "enter";

  //const wchar_t *path = L"/Users/jichi/opt/stream/Library/Dictionaries/hanja/dic6.txt";
  const wchar_t *path = L"/v2/v2kit/share/hanja/dic7.txt";
  //std::wstring s = L"공주";
  //std::wstring s = L"상냥한 곳은 바뀌지 않았어. 옛날은 좀 더 형분적인 표현(이었)였지만.";
  //std::wstring s = L"지금 무엇을 하고 있을까. 자신의 판단으로 대답해도 좋은 것인가 헤매었을 것이다.";

  // Sentence from http://ko.wikipedia.org/wiki/자유_콘텐츠
  // Ambiguity: 이용이
  // Supposed to be 利用이 instead of 이容易
  //std::wstring s = L"자유 콘텐츠는 저작권이 소멸된 퍼블릭 도메인은 물론, 저작권이 있지만 위 기준에 따라 자유롭게 이용이 허락된 콘텐츠도 포함한다.";
  std::wstring s = L"콘텐츠는";
  //s = L"감사합니다";
  //std::wstring s = L"容易이용이";
  //std::wstring s = L"【오쿠라 리소나】「미나톤이 우리 집을 나온 후의 이야기군요. 외동딸(이었)였으므로, 그렇다면 집에서 인귀로라고 해도 좋다고 하는 것이 된 것 같아」";
  //std::wstring s = L"【오쿠라 리소나】「미나톤이";

  //std::wstring s = L"test";
  //wchar_t ch = L'【';
  //wchar_t ch = L'「';
  //qDebug() << ::ispunct(ch) << QChar(ch).isPunct();

  HangulHanjaConverter conv;
  conv.loadFile(path);
  qDebug() << conv.size();

  std::wstring t = conv.convert(s.c_str());
  qDebug() << QString::fromStdWString(s);
  qDebug() << QString::fromStdWString(t);

  //std::list<std::pair<std::wstring, std::wstring> > l;
  //std::wstring text = s;
  //conv.collect(text.c_str(), text.size(), [&l, &text](size_t start, size_t length, const wchar_t *hanja) {
  //  l.push_back(std::make_pair(
  //    text.substr(start, length)
  //    , hanja ? std::wstring(hanja) : std::wstring()
  //  ));
  //});
  //s = L"hello";
  auto l = conv.parseToList(s);
  qDebug() << l.size();
  for (auto p = l.cbegin(); p != l.cend(); ++p)
    qDebug() << QString::fromStdWString(p->first) << ":" << QString::fromStdWString(p->second);

  qDebug() << "leave";
}

int main()
{
  test_hangul2hanja();
  test_hanja2hangul();
  return 0;
}

// EOF
