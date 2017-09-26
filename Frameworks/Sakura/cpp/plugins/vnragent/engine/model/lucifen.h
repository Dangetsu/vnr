#pragma once

// lucifen.h
// 7/26/2015 jichi

#include "engine/enginemodel.h"

class LucifenEngine : public EngineModel
{
  SK_EXTEND_CLASS(LucifenEngine, EngineModel)
  static bool attach();
  //static QString rubyCreate(const QString &rb, const QString &rt);
  //static QString rubyRemove(const QString &text);
public:
  LucifenEngine()
  {
    name = "EmbedLucifen";
    enableDynamicEncoding = true;
    enableDynamicFont = true;
    matchFiles << "*.lpk";
    scenarioLineCapacity = 40; // 62 in Prism Princess
    //newLineString = nullptr; // not enabled as newline works for other text but not work for scenario
    attachFunction = &Self::attach;
    //rubyCreateFunction = &Self::rubyCreate;
    //rubyRemoveFunction = &Self::rubyRemove;
  }
};

// EOF
