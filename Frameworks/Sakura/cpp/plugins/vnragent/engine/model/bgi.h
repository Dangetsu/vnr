#pragma once

// bgi.h
// 5/11/2014 jichi

#include "engine/enginemodel.h"

class BGIEngine : public EngineModel
{
  SK_EXTEND_CLASS(BGIEngine, EngineModel)
  static bool attach();
  static QString rubyCreate(const QString &rb, const QString &rt);
  static QString rubyRemove(const QString &text);
public:
  BGIEngine()
  {
    name = "EmbedBGI";
    enableDynamicEncoding = true;
    enableDynamicFont = true; // CreateFontIndirect only invoked once
    matchFiles << "BGI.*|BHVC.exe|sysgrp.arc";
    //newLineString = "\n";
    attachFunction = &Self::attach;
    rubyCreateFunction = &Self::rubyCreate;
    rubyRemoveFunction = &Self::rubyRemove;
  }
};

// EOF
