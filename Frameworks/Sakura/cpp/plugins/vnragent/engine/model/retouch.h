#pragma once

// retouch.h
// 6/20/2015 jichi

#include "engine/enginemodel.h"

class RetouchEngine : public EngineModel
{
  SK_EXTEND_CLASS(RetouchEngine, EngineModel)
  static bool attach();
public:
  RetouchEngine()
  {
    name = "EmbedRetouch";
    enableDynamicEncoding = true;
    enableDynamicFont = true; // hijack CreateFontIndirectA does not work
    //newLineString = "\n";
    matchFiles << "resident.dll"; // the process name is usually Exhibit.EXE.
    attachFunction = &Self::attach;
  }
};

// EOF
