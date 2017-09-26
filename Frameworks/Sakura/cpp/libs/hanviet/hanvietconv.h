#ifndef HANVIETCONV_H
#define HANVIETCONV_H

// hanvietconv.h
// 2/2/2015 jichi

#include "sakurakit/skglobal.h"
#include <string>
#include <functional>

class HanVietWordDictionary;
class HanVietPhraseDictionary;
class HanVietConverterPrivate;
class HanVietConverter
{
  SK_CLASS(HanVietConverter)
  SK_DISABLE_COPY(HanVietConverter)
  SK_DECLARE_PRIVATE(HanVietConverterPrivate)

  // - Construction -
public:
  HanVietConverter();
  ~HanVietConverter();

  HanVietWordDictionary *wordDicionary() const;
  HanVietPhraseDictionary *phraseDicionary() const;

  // Initialization

  ///  Clear the loaded script
  void clear();

  bool addWordFile(const std::wstring &path);
  bool addPhraseFile(const std::wstring &path);

  // Query

  size_t wordSize() const;
  size_t phraseSize() const;

  std::wstring lookupWord(int ch) const;
  std::wstring lookupPhrase(const std::wstring &text) const;

  // Replacement

  std::wstring toReading(const std::wstring &text) const;

  std::wstring translate(const std::wstring &text, bool mark = false) const;

  // Translate with alignment
  typedef std::function<void (const std::wstring &, const std::wstring &)> align_fun_t;
  std::wstring analyze(const std::wstring &text, bool mark = false,
                       const align_fun_t &align = align_fun_t()) const;
};

#endif // HANVIETCONV_H
