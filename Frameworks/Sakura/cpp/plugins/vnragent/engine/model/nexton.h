#pragma once

// nexton.h
// 7/30/2015 jichi

#include "engine/enginemodel.h"

class NextonEngine : public EngineModel
{
  SK_EXTEND_CLASS(NextonEngine, EngineModel)
  static bool attach();
public:
  NextonEngine()
  {
    name = "EmbedNexton";
    enableDynamicEncoding = true;
    enableDynamicFont = true;
    matchFiles << "aInfo.db";
    scenarioLineCapacity = 40; // 29 wide characters in InnocentBullet
    //newLineString = "\\n";
    attachFunction = &Self::attach;
  }
};

// EOF
