#pragma once

// escude.h
// 7/23/2015 jichi

#include "engine/enginemodel.h"

class EscudeEngine : public EngineModel
{
  SK_EXTEND_CLASS(EscudeEngine, EngineModel)
  static bool attach();
  static QString rubyCreate(const QString &rb, const QString &rt);
  static QString rubyRemove(const QString &text);
public:
  EscudeEngine()
  {
    name = "EmbedEscude";
    enableDynamicEncoding = true;
    enableDynamicFont = true;
    newLineString = "<r>";
    matchFiles << "configure.cfg" << "gfx.bin";
    attachFunction = &Self::attach;
    rubyCreateFunction = &Self::rubyCreate;
    rubyRemoveFunction = &Self::rubyRemove;
  }
};

// EOF
