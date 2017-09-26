#pragma once

// unicorn.h
// 6/22/2015 jichi

#include "engine/enginemodel.h"

//#define UNICORN_BR  "[n]"
class UnicornEngine : public EngineModel
{
  SK_EXTEND_CLASS(UnicornEngine, EngineModel)
  static bool attach();
public:
  UnicornEngine()
  {
    name = "EmbedUnicorn";
    enableDynamicEncoding = true;
    //enableDynamicFont = true;
    //newLineString = "\n";
    scenarioLineCapacity = 40; // around 26 kanji in 三極姫4
    otherLineCapacity = 20; // around 10 kanji in 戦極姫6
    matchFiles << "*.szs|data/*.szs";
    attachFunction = &Self::attach;
  }
};

// EOF
