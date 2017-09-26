#pragma once

// minori.h
// 8/29/2015 jichi

#include "engine/enginemodel.h"

class MinoriEngine : public EngineModel
{
  SK_EXTEND_CLASS(MinoriEngine, EngineModel)
  static bool attach();
  static QString rubyCreate(const QString &rb, const QString &rt);
  static QString rubyRemove(const QString &text);
public:
  MinoriEngine()
  {
    name = "EmbedMinori";
    enableDynamicEncoding = true;
    //enableDynamicFont = true;
    //newLineString = "\n";
    matchFiles << "*.paz";
    textSeparators << "\\N" << "\\a" << "\\v"; //<< "#";
    attachFunction = &Self::attach;
    rubyCreateFunction = &Self::rubyCreate;
    rubyRemoveFunction = &Self::rubyRemove;
  }
};

// EOF
