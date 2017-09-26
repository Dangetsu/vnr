#pragma once

// enginesettings.h
// 4/20/2014 jichi

#include "engine/enginedef.h"

class EngineSettings
{
public:
  bool enabled          // if vnragent is enabled
     //, detectsControl   // be aware if CTRL is pressed
     , alwaysInsertsSpaces  // insert spaces after every character
     , smartInsertsSpaces  // insert spaces after every character

     , extractsAllTexts     // send all texts unless not enabled
     , scenarioTextVisible  // display both translation and the original text for scenario
     , nameTextVisible      // display both translation and the original text for names
     , otherTextVisible     // display both translation and the original text for other texts

     , textVisible[Engine::RoleCount]           // if display/hide all texts
     , transcodingEnabled[Engine::RoleCount]    // if fix the encoding
     , translationEnabled[Engine::RoleCount]    // if display translation
     , extractionEnabled[Engine::RoleCount]     // if send text
  ;

  size_t scenarioCapacity, // maximum size of scenario
         nameCapacity,     // maximum size of name
         otherCapacity;    // maximum size of other text

  int scenarioWidth; // maximum thin character in a text line

  long scenarioSignature,
       nameSignature;

  // Set all properties to false
  EngineSettings()
    : enabled(false)

    , alwaysInsertsSpaces(false)
    , smartInsertsSpaces(false)

    , extractsAllTexts(false)
    , scenarioTextVisible(false)
    , nameTextVisible(false)
    , otherTextVisible(false)

    , scenarioCapacity(500)
    , nameCapacity(100)
    , otherCapacity(200)

    , scenarioWidth(0)

    , scenarioSignature(0)
    , nameSignature(0)
  {
    for (int role = 0; role < Engine::RoleCount; role++)
      textVisible[role]
      = transcodingEnabled[role]
      = translationEnabled[role]
      = extractionEnabled[role]
      = false;
  }

  Engine::TextRole textRoleOf(long signature) const
  {
    return !signature ? Engine::OtherRole :
        signature == scenarioSignature ? Engine::ScenarioRole :
        signature == nameSignature ? Engine::NameRole :
        Engine::OtherRole;
  }
};

// EOF
