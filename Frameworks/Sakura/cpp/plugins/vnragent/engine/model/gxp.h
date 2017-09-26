#pragma once

// gxp.h
// 8/15/2015 jichi

#include "engine/enginemodel.h"

class GXPEngine : public EngineModel
{
  SK_EXTEND_CLASS(GXPEngine, EngineModel)
  static bool attach();
  static QString rubyCreate(const QString &rb, const QString &rt);
  static QString rubyRemove(const QString &text);

public:
  GXPEngine()
  {
    name = "EmbedGXP";
    matchFiles << "*.gxp";
    encoding = Utf16Encoding;
    //enableDynamicFont = true;
    scenarioLineCapacity = 40;
    newLineString = "%r";
    textSeparators << "||"; // for other text in verethragna
    attachFunction = &Self::attach;
    //rubyCreateFunction = &Self::rubyCreate;
    //rubyRemoveFunction = &Self::rubyRemove;
  }
};

// EOF
