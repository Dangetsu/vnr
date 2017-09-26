#pragma once

// wolf.h
// 6/9/2015 jichi

#include "engine/enginemodel.h"

class WolfRPGEngine : public EngineModel
{
  SK_EXTEND_CLASS(WolfRPGEngine, EngineModel)
  static bool attach();
  //static QString textFilter(const QString &text, int role);
public:
  WolfRPGEngine()
  {
    name = "EmbedWolfRPG";
    enableDynamicEncoding = true;
    enableDynamicFont = true;
    matchFiles << "data.wolf|data/*.wolf";
    //newLineString = "\n";
    attachFunction = &Self::attach;
    //textFilterFunction = &Self::textFilter;
  }
};

// EOF
