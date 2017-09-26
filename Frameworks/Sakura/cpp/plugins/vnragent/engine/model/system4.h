#pragma once

// system4.h
// 5/25/2015 jichi

#include "engine/enginemodel.h"

// Single thread
class System4Engine : public EngineModel
{
  SK_EXTEND_CLASS(System4Engine, EngineModel)
  bool attach();

  static bool attachSystem43(ulong startAddress, ulong stopAddress);
  static bool attachSystem44(ulong startAddress, ulong stopAddress);
public:
  System4Engine()
  {
    name = "EmbedSystem4";
    //enableDynamicEncoding = true;
    matchFiles << "AliceStart.ini";
    newLineString = nullptr;
    attachFunction = std::bind(&Self::attach, this);
    textSeparators << "|"; // only for other texts
  }
};

// EOF
