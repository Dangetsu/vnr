#pragma once

// luna.h
// 8/2/2015 jichi

#include "engine/enginemodel.h"

class LunaSoftEngine : public EngineModel
{
  SK_EXTEND_CLASS(LunaSoftEngine, EngineModel)
  static bool attach();
public:
  LunaSoftEngine()
  {
    name = "EmbedLunaSoft";
    //enableDynamicEncoding = true;
    enableDynamicFont = true;
    matchFiles << "Pac/*.pac";
    //newLineString = "\n";
    scenarioLineCapacity = 40; // around 50 in 悪堕ラビリンス
    attachFunction = &Self::attach;
  }
};

// EOF
