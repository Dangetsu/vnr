#pragma once

// qlie.h
// 7/5/2015 jichi

#include "engine/enginemodel.h"

class QLiEEngine : public EngineModel
{
  SK_EXTEND_CLASS(QLiEEngine, EngineModel)
  static bool attach();
  static QString textFilter(const QString &text, int role);
  static QString translationFilter(const QString &text, int role);
  static QString rubyCreate(const QString &rb, const QString &rt);
  static QString rubyRemove(const QString &text);

public:
  QLiEEngine()
  {
    name = "EmbedQLiE";
    enableDynamicEncoding = true;
    newLineString = "[n]";
    matchFiles << "GameData/data*.pack"; // mostly data0.pack, data1.pack, ...
    attachFunction = &Self::attach;
    textFilterFunction = &Self::textFilter;
    translationFilterFunction = &Self::translationFilter;
    rubyCreateFunction = &Self::rubyCreate;
    rubyRemoveFunction = &Self::rubyRemove;
  }
};

// EOF
