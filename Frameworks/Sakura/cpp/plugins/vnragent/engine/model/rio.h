#pragma once

// rio.h
// 7/10/2015 jichi

#include "engine/enginemodel.h"

class ShinaRioEngine : public EngineModel
{
  SK_EXTEND_CLASS(ShinaRioEngine, EngineModel)
  static bool attach();
  static QString textFilter(const QString &text, int role);
  static QString rubyCreate(const QString &rb, const QString &rt);
  static QString rubyRemove(const QString &text);

public:
  ShinaRioEngine()
  {
    name = "EmbedRio";
    enableDynamicEncoding = true;
    newLineString = "_r";
    matchFiles << "*.war";
    scenarioLineCapacity =
    otherLineCapacity = 40; // 60 in 3rd games (30 wide characters)
    attachFunction = &Self::attach;
    //rubyCreateFunction = &Self::rubyCreate; // FIXME: does not work
    rubyRemoveFunction = &Self::rubyRemove;
  }
};

// EOF
