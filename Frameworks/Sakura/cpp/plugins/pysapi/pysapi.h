#ifndef PYSAPI_H
#define PYSAPI_H

// pysapi.h
// 4/7/2013 jichi

#include "sakurakit/skglobal.h"
#include <string>

class SapiPlayer_p;
class SapiPlayer
{
  SK_CLASS(SapiPlayer)
  SK_DISABLE_COPY(SapiPlayer)
  SK_DECLARE_PRIVATE(SapiPlayer_p)

public:
  // Construction
  //
  SapiPlayer();
  ~SapiPlayer();

  bool isValid() const;

  // Example registry: L"HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Speech\\Voices\\Tokens\\VW Misaki"
  bool setVoice(const std::wstring &registry);
  std::wstring voice() const;
  bool hasVoice() const;

  // Actions

  bool speak(const std::wstring &text, bool async = false) const;
  bool purge(bool async = false) const; // clear previous speak
};

#endif // PYSAPI_H
