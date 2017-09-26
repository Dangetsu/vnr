// hanvietconv.cc
// 2/2/2015 jichi

#include "hanviet/hanvietconv.h"
#include "hanviet/phrasedic.h"
#include "hanviet/worddic.h"
#include "unistr/unistr.h"
#include <functional> // for bind
//#include <iostream>
//#include <QDebug>

using namespace std::placeholders; // for _1, _2, etc.

/** Private class */

class HanVietConverterPrivate
{
public:
  HanVietWordDictionary *wordDic;
  HanVietPhraseDictionary *phraseDic;

  HanVietConverterPrivate()
    : wordDic(new HanVietWordDictionary)
    , phraseDic(new HanVietPhraseDictionary)
  {}

  ~HanVietConverterPrivate()
  {
    delete wordDic;
    delete phraseDic;
  }
};

/** Public class */

// Construction

HanVietConverter::HanVietConverter() : d_(new D) {}
HanVietConverter::~HanVietConverter() { delete d_; }

void HanVietConverter::clear()
{
  d_->wordDic->clear();
  d_->phraseDic->clear();
}

HanVietWordDictionary *HanVietConverter::wordDicionary() const
{ return d_->wordDic; }

HanVietPhraseDictionary *HanVietConverter::phraseDicionary() const
{ return d_->phraseDic; }

size_t HanVietConverter::wordSize() const
{ return d_->wordDic->size(); }

size_t HanVietConverter::phraseSize() const
{ return d_->phraseDic->size(); }

bool HanVietConverter::addWordFile(const std::wstring &path)
{ return d_->wordDic->addFile(path); }

bool HanVietConverter::addPhraseFile(const std::wstring &path)
{ return d_->phraseDic->addFile(path); }

// Conversion

std::wstring HanVietConverter::lookupWord(int ch) const
{ return d_->wordDic->lookup(ch); }

std::wstring HanVietConverter::lookupPhrase(const std::wstring &text) const
{ return d_->phraseDic->lookup(text); }

std::wstring HanVietConverter::toReading(const std::wstring &text) const
{ return d_->wordDic->translate(text); }

std::wstring HanVietConverter::translate(const std::wstring &text, bool mark) const
{
  std::wstring ret = d_->phraseDic->translate(text, mark);
  ret = d_->wordDic->translate(ret);
  unistr::to_thin(ret);
  return ret;
}

std::wstring HanVietConverter::analyze(const std::wstring &text, bool mark, const align_fun_t &align) const
{
  //unistr::to_thin(text); // not applied
  auto fallback = std::bind(&HanVietWordDictionary::translate, d_->wordDic, _1);
  return d_->phraseDic->analyze(text, mark, align, fallback);
}

// EOF
