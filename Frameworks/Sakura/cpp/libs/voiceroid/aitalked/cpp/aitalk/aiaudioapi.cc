// aiaudioapi.cc
// 10/12/2014 jichi
#include "aitalk/aiaudioapi.h"
#include <windows.h>

bool AITalk::AIAudioAPI::LoadModule(HMODULE h)
{
#define get(var) \
  (var = (AIAudioAPI_##var)::GetProcAddress(h, _AIAudioAPI_##var))
  get(ClearData);
  get(Close);
  get(Open);
  get(PushData);
  get(PushEvent);
  get(Resume);
  get(SaveWave);
  get(Suspend);
#undef get

  return IsValid();
}

// EOF
