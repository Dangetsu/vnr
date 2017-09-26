#pragma once

// fvp.h
// 7/28/2015 jichi

#include "engine/enginemodel.h"

class FVPEngine : public EngineModel
{
  SK_EXTEND_CLASS(FVPEngine, EngineModel)
  static bool attach();
  static QString rubyCreate(const QString &rb, const QString &rt);
  static QString rubyRemove(const QString &text);

public:
  FVPEngine()
  {
    name = "EmbedFVP";
    matchFiles << "*.hcb";
    enableDynamicEncoding = true;
    enableDynamicFont = true;
    newLineString = nullptr;
    attachFunction = &Self::attach;
    rubyCreateFunction = &Self::rubyCreate;
    rubyRemoveFunction = &Self::rubyRemove;
  }
};

// EOF
