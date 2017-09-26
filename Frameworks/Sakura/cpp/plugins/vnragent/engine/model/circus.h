#pragma once

// circus.h
// 6/4/2014 jichi

#include "engine/enginemodel.h"

// Currently, only CIRCUS Type#2 is implemented
// I don't know any Type#1 games
class CircusEngine : public EngineModel
{
  SK_EXTEND_CLASS(CircusEngine, EngineModel)
  static bool attach();
  static QString rubyCreate(const QString &rb, const QString &rt);
  static QString rubyRemove(const QString &text);

public:
  CircusEngine()
  {
    name = "EmbedCircus";
    matchFiles << "AdvData/GRP/NAMES.DAT"; // New circus games
    //matchFiles << "AdvData/DAT/NAMES.DAT"; // Old circus games
    //enableDynamicEncoding = true;
    //newLineString = "\n";
    scenarioLineCapacity =
    otherLineCapacity = 40; // 61 in D.C.III, around 50 in 水夏弐律(vertical)
    attachFunction = &Self::attach;
    //rubyCreateFunction = &Self::rubyCreate; // ruby only works for double-width characters
    rubyRemoveFunction = &Self::rubyRemove;
  }
};

// EOF

    // TODO: Unify the text/size/split asm
    //textAsm("[esp+8]")  // arg2
    //sizeAsm(nullptr)  // none
    //splitAsm("[esp]") // return address

