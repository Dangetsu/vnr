#pragma once

// cs2.h
// 6/21/2015 jichi

#include "engine/enginemodel.h"

class CatSystemEngine : public EngineModel
{
  SK_EXTEND_CLASS(CatSystemEngine, EngineModel)
  bool attach();
  static QString rubyCreate(const QString &rb, const QString &rt);
  static QString rubyRemove(const QString &text);
  static QString translationFilter(const QString &text, int role);
public:
  CatSystemEngine()
  {
    name = "EmbedCatSystem2";
    //enableDynamicEncoding = true;
    enableDynamicFont = true;
    matchFiles << "*.int";
    textSeparators << "\\pc" << "\\@";
    newLineString = "\\n";
    attachFunction = std::bind(&Self::attach, this);
    rubyCreateFunction = &Self::rubyCreate;
    rubyRemoveFunction = &Self::rubyRemove;
    translationFilterFunction = &Self::translationFilter;
  }
};

// EOF
