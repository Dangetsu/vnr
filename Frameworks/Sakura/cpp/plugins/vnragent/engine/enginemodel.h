#pragma once

// enginemodel.h
// 6/10/2014 jichi

#include "sakurakit/skglobal.h"
#include <QtCore/QStringList>
#include <functional>

class EngineModel
{
  SK_CLASS(EngineModel)
public:
  enum Encoding {
    AsciiEncoding = 0,
    Utf16Encoding,
    Utf8Encoding,
  };

  EngineModel()
    : name(nullptr)
    , encoding(AsciiEncoding)       // scenario thread encoding

    , enableLocaleEmulation(false)  // fix inconsistent game locale
    , enableDynamicFont(false)      // change GDI device context font
    , enableDynamicEncoding(false)  // whether use dynamic codec to fix ascii text
    , enableNonDecodableCharacters(false) // allow having non-encodable characters
    , enableThin2WideCharacters(false)     // Force using wide character in the translation
    , dynamicEncodingMinimumByte(0) // minimum value for the dynamic sjis

    , scenarioLineCapacity(0)       // estimated maximum number of thin characters for scenario text per line, 0 to disable it
    , otherLineCapacity(0)          // estimated maximum number of thin characters for other text per line, 0 to disable it
    , newLineString("\n")           // new line deliminator, nullptr if does not work
    , separatorString(" / ")        // text separator

    //, matchFunction(nullptr)      // determine whether apply engine
    //, attachFunction(nullptr)     // apply the engine
    //, detachFunction(nullptr)     // remove the applied engine
    , textFilterFunction(nullptr)   // fix scenario text before sending out
    , translationFilterFunction(nullptr)    // fix translation text before sending out
    , rubyCreateFunction(nullptr)
    , rubyRemoveFunction(nullptr)
  {}

  const char *name;
  Encoding encoding;
  bool enableLocaleEmulation,
       enableDynamicFont,
       enableDynamicEncoding,
       enableNonDecodableCharacters;

  bool enableThin2WideCharacters;

  int dynamicEncodingMinimumByte;

  int scenarioLineCapacity,
      otherLineCapacity;

  const char *newLineString,
             *separatorString;

  QStringList matchFiles; // files existing in the game directory

  QStringList textSeparators; // strings that will split sentences

  // Global match functions
  //typedef bool (* match_function)();
  typedef std::function<bool ()> match_function;
  match_function matchFunction, // override match files
                 attachFunction, // override searchFunction and hookFunction
                 detachFunction; // not used

  // Text functions
  typedef QString (* filter_function)(const QString &text, int role);
  filter_function textFilterFunction,        ///< modify game text
                  translationFilterFunction; ///< modify translation

  typedef QString (* text_function)(const QString &x);
  typedef QString (* text2_function)(const QString &x, const QString &y);

  text2_function rubyCreateFunction; ///< create ruby
  text_function rubyRemoveFunction; ///< remove ruby
};

  // Memory search function
  //typedef ulong (* search_function)(ulong startAddress, ulong stopAddress);
  //search_function searchFunction; ///< return the hook address

  //// Hijacked function
  //struct HookStack
  //{
  //  ulong eflags;  // pushaf
  //  ulong edi,     // pushad
  //        esi,
  //        ebp,
  //        esp,
  //        ebx,
  //        edx,
  //        ecx,     // this
  //        eax;     // 0x24
  //  ulong retaddr; // 0x2c, &retaddr == esp
  //  ulong args[1]; // 0x2e
  //};
  //typedef void (* hook_function)(HookStack *);
  //hook_function hookFunction; ///< callback of hooked function

// EOF
