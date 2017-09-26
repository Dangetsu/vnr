#pragma once

// malie.h
// 8/8/2015 jichi

#include "engine/enginemodel.h"

#define MALIE_0  L"[0]" // represent \0
class MalieEngine : public EngineModel
{
  SK_EXTEND_CLASS(MalieEngine, EngineModel)
  static bool attach();
  static QString rubyCreate(const QString &rb, const QString &rt);
  //static QString rubyRemove(const QString &text); // already removed
public:
  MalieEngine()
  {
    name = "EmbedMalie";
    encoding = Utf16Encoding;
    //enableDynamicFont = true;
    //newLineString = "\n";
    matchFiles << "Malie*"; // Malie.ini or Malie.exe or MalieCfg.exe
    attachFunction = &Self::attach;
    rubyCreateFunction = &Self::rubyCreate;
  }
};

// EOF
