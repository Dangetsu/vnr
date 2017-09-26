#pragma once

// yuka.h
// 7/19/2015 jichi

#include "engine/enginemodel.h"

class YukaSystemEngine : public EngineModel
{
  SK_EXTEND_CLASS(YukaSystemEngine, EngineModel)
  static bool attach();

public:
  YukaSystemEngine()
  {
    name = "EmbedYukaSystem";
    //enableDynamicEncoding = true;
    encoding = Utf8Encoding;
    //newLineString = nullptr;
    matchFiles << "*.ykc";
    attachFunction = &Self::attach;
  }
};

// EOF
