#pragma once

// waffle.h
// 8/18/2015 jichi

#include "engine/enginemodel.h"

class WaffleEngine : public EngineModel
{
  SK_EXTEND_CLASS(WaffleEngine, EngineModel)
  static bool attach();

public:
  WaffleEngine()
  {
    name = "EmbedWaffle";
    matchFiles << "cfg.pak";
    enableDynamicEncoding = true;
    scenarioLineCapacity = 40;
    //enableDynamicFont = true;
    //newLineString = "\n";
    attachFunction = &Self::attach;
  }
};

// EOF
