#pragma once

// horkeye.h
// 6/24/2015 jichi
//
// FIXME: Engine does not work as it would crash when get modified

#include "engine/enginemodel.h"

class HorkEyeEngine : public EngineModel
{
  SK_EXTEND_CLASS(HorkEyeEngine, EngineModel)
  static bool attach();
  static QString textFilter(const QString &text, int role);
  static QString translationFilter(const QString &text, int role);
public:
  HorkEyeEngine()
  {
    name = "EmbedHorkEye";
    //enableDynamicEncoding = true;
    matchFiles << "arc0.dat" << "arc1.dat" << "arc2.dat" << "script.dat";
    newLineString = "[n]";
    //scenarioLineCapacity = 40; // at least 25 wide character
    attachFunction = &Self::attach;
  }
};

// EOF
