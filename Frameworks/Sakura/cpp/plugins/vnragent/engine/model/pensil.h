#pragma once

// pensil.h
// 8/1/2015 jichi

#include "engine/enginemodel.h"

class PensilEngine : public EngineModel
{
  SK_EXTEND_CLASS(PensilEngine, EngineModel)
  static bool attach();
  static QString rubyCreate(const QString &rb, const QString &rt);
  static QString rubyRemove(const QString &text);
public:
  PensilEngine()
  {
    name = "EmbedPensil";
    enableDynamicEncoding = true;
    enableDynamicFont = true;
    //newLineString = "\n";
    matchFiles << "PSetup.exe|MovieTexture.dll|PENCIL.*"; // || Util::SearchResourceString(L"2XT -") || Util::SearchResourceString(L"2RM -")
    attachFunction = &Self::attach;
    rubyCreateFunction = &Self::rubyCreate; // ruby only works for double-width characters
    rubyRemoveFunction = &Self::rubyRemove;
  }
};

// EOF
