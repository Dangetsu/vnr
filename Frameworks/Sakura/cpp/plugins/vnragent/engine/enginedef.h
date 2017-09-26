#pragma once

// enginedef.h
// 4/26/2014 jichi

namespace Engine {

// These values must be consistent with VNR's textman.py
enum TextRole { UnknownRole = 0, ScenarioRole,  NameRole, OtherRole,
                ChoiceRole = OtherRole, HistoryRole = OtherRole,
                RoleCount };

// Dummy fixed signature the same as ITH for single text thread
enum {
  SingleThreadSignatureBase = 0x10000
  , ScenarioThreadSignature = SingleThreadSignatureBase
  , NameThreadSignature = SingleThreadSignatureBase << 1
  , OtherThreadSignature = SingleThreadSignatureBase << 2
};

// Emperical maximum memory range of an application
//enum { MaximumMemoryRange = 0x300000 };

} // namespace Engine

// EOF
