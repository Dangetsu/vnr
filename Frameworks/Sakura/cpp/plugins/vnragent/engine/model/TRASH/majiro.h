#pragma once

// majiro.h
// 4/20/2014 jichi

#include "engine/enginemodel.h"

class MajiroEngine : public EngineModel
{
  SK_EXTEND_CLASS(MajiroEngine, EngineModel)
  static ulong search(ulong startAddress, ulong stopAddress);
  static void hook(HookStack *stack);
public:
  MajiroEngine()
  {
    name = "Majiro";
    matchFiles << "data*.arc" << "stream*.arc";
    searchFunction = &Self::search;
    hookFunction = &Self::hook;
  }
};

// EOF
