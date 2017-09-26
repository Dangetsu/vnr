#pragma once

// sideb.h
// 8/2/2014 jichi

#include "engine/enginemodel.h"

class SideBEngine : public EngineModel
{
  SK_EXTEND_CLASS(SideBEngine, EngineModel)
  static ulong startAddress_; // backup of startAddress
  static ulong search(ulong startAddress, ulong stopAddress);
  static void hook(HookStack *stack);
public:
  SideBEngine() //BlockingAttribute|SingleThreadAttribute)
  {
    name = "SideB";
    //matchResourceStrings << "side-B"; // matchString is not implemented yet
    matchFiles << "lua5.1.dll" << "dat/0001.dat";
    searchFunction = &Self::search;
    hookFunction = &Self::hook;
  }
};

// EOF
