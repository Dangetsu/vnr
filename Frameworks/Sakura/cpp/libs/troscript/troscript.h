#ifndef TROSCRIPT_H
#define TROSCRIPT_H

// troscript.h
// 5/17/2015 jichi

#include "sakurakit/skglobal.h"
#include <string>

class TranslationOutputScriptPerformerPrivate;
class TranslationOutputScriptPerformer
{
  SK_CLASS(TranslationOutputScriptPerformer)
  SK_DISABLE_COPY(TranslationOutputScriptPerformer)
  SK_DECLARE_PRIVATE(TranslationOutputScriptPerformerPrivate)

  // - Construction -
public:
  TranslationOutputScriptPerformer();
  ~TranslationOutputScriptPerformer();

  // Initialization

  ///  Return the number of loaded rules
  int size() const;

  ///  Return whether the script has been loaded, thread-safe
  bool isEmpty() const;

  ///  Clear the loaded script
  void clear();

  ///  Add script from file
  bool loadScript(const std::wstring &path);

  // Replacement

  // Rewrite the text according to the script, thread-safe
  std::wstring transform(const std::wstring &text, int category = -1, bool mark = false) const;

  // Render option

  //std::wstring linkStyle() const;
  //void setLinkStyle(const std::wstring &css);
};

#endif // TROSCRIPT_H
