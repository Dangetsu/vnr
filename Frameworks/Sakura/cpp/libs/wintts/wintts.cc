// wintts.cc
// 4/7/2013 jichi

#include "wintts/wintts.h"
#include <windows.h>
#include <sapi.h>
#include "ccutil/ccmacro.h"

wintts_t *wintts_create()
{
  ISpVoice *ret = nullptr;
  return SUCCEEDED(::CoCreateInstance(CLSID_SpVoice, nullptr, CLSCTX_ALL, IID_ISpVoice,
      reinterpret_cast<LPVOID *>(&ret))) ? ret : nullptr;
}

void wintts_destroy(wintts_t *voice)
{
  // FIXME: voice's token is not destroyed?
  if (CC_LIKELY(voice))
    voice->Release();
}

bool wintts_set_voice(wintts_t *voice, const wchar_t *reg)
{
  if (CC_UNLIKELY(!voice || !reg))
    return false;

  enum { fCreateIfNotExist = FALSE };
  ISpObjectToken *token;
  if (SUCCEEDED(::CoCreateInstance(CLSID_SpObjectToken, nullptr, CLSCTX_ALL, IID_ISpObjectToken,
          reinterpret_cast<LPVOID *>(&token)))) {
    if (SUCCEEDED(token->SetId(nullptr, reg, fCreateIfNotExist))) {
      voice->SetVoice(token);
      return true;
    }
    token->Release();
  }
  return false;
}

bool wintts_speak(wintts_t *voice, const wchar_t *text, unsigned long flags)
{ return voice && SUCCEEDED(voice->Speak(text, flags, nullptr)); }

// EOF
