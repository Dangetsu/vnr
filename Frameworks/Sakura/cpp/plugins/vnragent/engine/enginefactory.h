#pragma once

// enginefactory.h
// 4/26/2014 jichi

class EngineController;
class EngineFactory
{
public:
  static EngineController *createEngine();
};

// EOF
