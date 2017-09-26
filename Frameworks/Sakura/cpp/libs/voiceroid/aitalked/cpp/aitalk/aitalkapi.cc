// aitalkapi.cc
// 10/11/2014 jichi
#include "aitalk/aitalkapi.h"
#include <windows.h>

/* Global variables */

bool AITalk::AITalkAPI::LoadModule(HMODULE h)
{
#define get(var) \
  (var =(AITalkAPI_##var)::GetProcAddress(h, _AITalkAPI_##var))
  get(BLoadWordDic);
  get(CloseKana);
  get(CloseSpeech);
  get(End);
  get(GetData);
  get(GetJeitaControl);
  get(GetParam);
  get(GetStatus);
  get(Init);
  get(LangClear);
  get(LangLoad);
  get(ReloadPhraseDic);
  get(ReloadSymbolDic);
  get(ReloadWordDic);
  get(SetParam);
  get(TextToKana);
  get(TextToSpeech);
  get(VersionInfo);
  get(VoiceClear);
  get(VoiceLoad);
#undef get

  return IsValid();
}

// EOF
