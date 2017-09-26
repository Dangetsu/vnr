#pragma once

// nexas.h
// 7/6/2014 jichi

#include "engine/enginemodel.h"

class NeXASEngine : public EngineModel
{
  SK_EXTEND_CLASS(NeXASEngine, EngineModel)
  static bool attach();
  static ulong search(ulong startAddress, ulong stopAddress);
  static void hook(HookStack *stack);
public:
  NeXASEngine()
  {
    name = "NeXAS";
    matchFiles << "Thumbnail.pac";
    //attachFunction = &Self::attach;
    searchFunction = &Self::search;
    hookFunction = &Self::hook;
  }
};

// EOF
