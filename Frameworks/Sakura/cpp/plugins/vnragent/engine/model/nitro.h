#pragma once

// nitro.h
// 11/22/2014 jichi

#include "engine/enginemodel.h"

class NitroplusEngine : public EngineModel
{
  SK_EXTEND_CLASS(NitroplusEngine, EngineModel)
  static bool attach();
  static QString textFilter(const QString &text, int role);
public:
  NitroplusEngine()
  {
    name = "EmbedNitroplus";
    //enableDynamicEncoding = true; // FIXME: English only
    enableThin2WideCharacters = true; // FIXME: English font issue
    matchFiles << "*.npk";
    //newLineString = "\n";
    attachFunction = &Self::attach;
  }
};

// EOF
