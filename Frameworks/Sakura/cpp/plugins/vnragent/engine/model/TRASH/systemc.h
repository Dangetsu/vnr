#pragma once

// systemc.h
// 6/30/2015 jichi
//
// FIXME: This engine does not work as text is broken into lines.

#include "engine/enginemodel.h"

class SystemCEngine : public EngineModel
{
  SK_EXTEND_CLASS(SystemCEngine, EngineModel)
  static bool attach();

public:
  SystemCEngine()
  {
    name = "EmbedSystemC";
    //enableDynamicEncoding = true;
    matchFiles << "*.fpk|data/*.fpk";
    attachFunction = &Self::attach;
    //rubyCreateFunction = &Self::rubyCreate;
    //rubyRemoveFunction = &Self::rubyRemove;
  }
};

// EOF
