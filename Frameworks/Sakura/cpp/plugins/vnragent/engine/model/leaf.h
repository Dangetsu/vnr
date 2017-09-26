#pragma once

// leaf.h
// 6/24/2015 jichi

#include "engine/enginemodel.h"

class LeafEngine : public EngineModel
{
  SK_EXTEND_CLASS(LeafEngine, EngineModel)
  static bool attach();
  static QString textFilter(const QString &text, int role);
  static QString rubyCreate(const QString &rb, const QString &rt);
  static QString rubyRemove(const QString &text);
public:
  LeafEngine()
  {
    name = "EmbedLeaf";
    //enableDynamicEncoding = true;
    scenarioLineCapacity = 40; // 26 wide characters in White Album 2
    matchFiles << "bak.pak";
    newLineString = "\\n";
    attachFunction = &Self::attach;
    textFilterFunction = &Self::textFilter;
    rubyCreateFunction = &Self::rubyCreate;
    rubyRemoveFunction = &Self::rubyRemove;
  }
};

// EOF
