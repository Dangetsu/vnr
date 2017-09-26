#pragma once

// krkrz.h
// 6/15/2015 jichi

#include "engine/enginemodel.h"

class KiriKiriZEngine : public EngineModel
{
  SK_EXTEND_CLASS(KiriKiriZEngine, EngineModel)
  static bool attach();
  static QString textFilter(const QString &text, int role);
public:
  KiriKiriZEngine()
  {
    name = "EmbedKiriKiriZ";
    encoding = Utf16Encoding;
    matchFiles << "plugin/textrender.dll";
    attachFunction = &Self::attach;
    textFilterFunction = &Self::textFilter;
  }
};

// EOF
