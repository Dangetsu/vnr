#pragma once

// debonosu.h
// 6/18/2015 jichi

#include "engine/enginemodel.h"

class DebonosuEngine : public EngineModel
{
  SK_EXTEND_CLASS(DebonosuEngine, EngineModel)
  static bool attach();
  static QString rubyCreate(const QString &rb, const QString &rt);
  static QString rubyRemove(const QString &text);
public:
  DebonosuEngine()
  {
    name = "EmbedDebonosu";
    enableDynamicEncoding = true;
    enableLocaleEmulation = true; // fix thread codepage in MultiByteToWideChar
    matchFiles << "bmp.pak" << "dsetup.dll";
    //newLineString = "\n";
    attachFunction = &Self::attach;
    rubyCreateFunction = &Self::rubyCreate;
    rubyRemoveFunction = &Self::rubyRemove;
  }
};

// EOF
