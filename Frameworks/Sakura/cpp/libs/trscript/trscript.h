#ifndef TRSCRIPT_H
#define TRSCRIPT_H

// trscript.h
// 9/20/2014 jichi

#include "sakurakit/skglobal.h"
#include <string>

class TranslationScriptPerformerPrivate;
class TranslationScriptPerformer
{
  SK_CLASS(TranslationScriptPerformer)
  SK_DISABLE_COPY(TranslationScriptPerformer)
  SK_DECLARE_PRIVATE(TranslationScriptPerformerPrivate)

  // - Construction -
public:
  TranslationScriptPerformer();
  ~TranslationScriptPerformer();

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

#endif // TRSCRIPT_H
