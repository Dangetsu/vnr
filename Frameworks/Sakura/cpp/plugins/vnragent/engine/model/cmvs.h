#pragma once

// cmvs.h
// 6/30/2015 jichi

#include "engine/enginemodel.h"

class CMVSEngine : public EngineModel
{
  SK_EXTEND_CLASS(CMVSEngine, EngineModel)
  static bool attach();

public:
  CMVSEngine()
  {
    name = "EmbedCMVS";
    enableDynamicEncoding = true;
    //newLineString = "\n";
    matchFiles << "data/pack/*.cpz";
    attachFunction = &Self::attach;
  }
};

// EOF
