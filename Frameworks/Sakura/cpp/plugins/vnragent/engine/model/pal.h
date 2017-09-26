#pragma once

// pal.h
// 7/18/2015 jichi

#include "engine/enginemodel.h"

class PalEngine : public EngineModel
{
  SK_EXTEND_CLASS(PalEngine, EngineModel)
  static bool attach();
  static QString textFilter(const QString &text, int role);
  static QString rubyCreate(const QString &rb, const QString &rt);
  static QString rubyRemove(const QString &text);

public:
  PalEngine()
  {
    name = "EmbedPal";
    //enableDynamicEncoding = true;
    newLineString = nullptr;
    matchFiles << "dll/Pal.dll";
    attachFunction = &Self::attach;
    textFilterFunction = &Self::textFilter;
    rubyCreateFunction = &Self::rubyCreate;
    rubyRemoveFunction = &Self::rubyRemove;
  }
};

// EOF
