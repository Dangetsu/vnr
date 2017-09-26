#pragma once

// will.h
// 7/3/2015 jichi

#include "engine/enginemodel.h"

class WillPlusEngine : public EngineModel
{
  SK_EXTEND_CLASS(WillPlusEngine, EngineModel)
  bool attach();
  static QString rubyCreate(const QString &rb, const QString &rt);
  static QString rubyRemove(const QString &text);

public:
  WillPlusEngine()
  {
    name = "EmbedWillPlus";
    //enableDynamicEncoding = true; // dynamically update this value
    newLineString = "\\n";
    matchFiles << "Rio.arc" << "Chip*.arc";
    attachFunction = std::bind(&Self::attach, this);
    rubyCreateFunction = &Self::rubyCreate;
    rubyRemoveFunction = &Self::rubyRemove;
  }
};

// EOF
