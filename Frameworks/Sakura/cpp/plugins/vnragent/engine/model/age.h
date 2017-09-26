#pragma once

// age.h
// 6/1/2014 jichi

#include "engine/enginemodel.h"

class ARCGameEngine : public EngineModel
{
  SK_EXTEND_CLASS(ARCGameEngine, EngineModel)
  static bool attach();
  static QString textFilter(const QString &text, int role);
public:
  ARCGameEngine()
  {
    name = "EmbedARCGameEngine";
    enableDynamicEncoding = true;
    enableNonDecodableCharacters = true; // there could be illegal characters even in scenario
    matchFiles << "AGERC.DLL"; // the process name is AGE.EXE.
    newLineString = nullptr;
    attachFunction = &Self::attach;
    textFilterFunction = &Self::textFilter;
  }
};

// EOF
