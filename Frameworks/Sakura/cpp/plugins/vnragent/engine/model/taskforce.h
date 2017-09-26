#pragma once

// taskforce.h
// 8/4/2015 jichi

#include "engine/enginemodel.h"

class TaskforceEngine : public EngineModel
{
  SK_EXTEND_CLASS(TaskforceEngine, EngineModel)
  static bool attach();
public:
  TaskforceEngine()
  {
    name = "EmbedTaskforce2";
    enableDynamicEncoding = true;
    enableDynamicFont = true;
    //newLineString = "\n";
    matchFiles << "Taskforce2.exe";
    attachFunction = &Self::attach;
  }
};

// EOF
