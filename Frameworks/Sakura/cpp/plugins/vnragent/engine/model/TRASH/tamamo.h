#pragma once

// tamamo.h
// 8/23/2015 jichi

#include "engine/enginemodel.h"

class TamamoEngine : public EngineModel
{
  SK_EXTEND_CLASS(TamamoEngine, EngineModel)
  static bool attach();

public:
  TamamoEngine()
  {
    name = "EmbedTamamo";
    matchFiles << "sprite.pck" << "voice.pck";
    enableDynamicEncoding = true;
    //enableDynamicFont = true;
    scenarioLineCapacity = 40;
    //newLineString = "\n";
    textSeparators << "<e>";
    attachFunction = &Self::attach;
  }
};

// EOF
