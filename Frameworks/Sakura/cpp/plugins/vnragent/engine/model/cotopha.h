#pragma once

// cotopha.h
// 6/30/2015 jichi

#include "engine/enginemodel.h"

class CotophaEngine : public EngineModel
{
  SK_EXTEND_CLASS(CotophaEngine, EngineModel)
  static bool attach();

public:
  CotophaEngine()
  {
    name = "EmbedCotopha";
    encoding = Utf16Encoding;
    //newLineString = "\n";
    matchFiles << "*.noa|data/*.noa";
    attachFunction = &Self::attach;
  }
};

// EOF
