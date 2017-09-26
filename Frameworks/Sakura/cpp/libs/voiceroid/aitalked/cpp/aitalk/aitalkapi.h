#pragma once

// aitalkapi.h
// 10/11/2014 jichi
#include "aitalk/aitalkdef.h"
#include "aitalk/_windef.h" // for HMODULE
#include <sal.h> // for _Out_

namespace AITalk
{

/* Exported DLL functions of aitalked.dll */

// Initialization

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_Init")]
// public static extern AITalkResultCode Init(ref AITalk_TConfig config);
#define _AITalkAPI_Init "_AITalkAPI_Init@4"
typedef AITalkResultCode (__stdcall *AITalkAPI_Init)(const AITalk_TConfig *config);

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_End")]
// private static extern AITalkResultCode _End();
#define _AITalkAPI_End "_AITalkAPI_End@0"
typedef AITalkResultCode (__stdcall *AITalkAPI_End)();

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_VersionInfo")]
// private static extern AITalkResultCode _VersionInfo(int verbose, StringBuilder sjis, uint len, out uint size);
#define _AITalkAPI_VersionInfo "_AITalkAPI_VersionInfo@16"
typedef AITalkResultCode (__stdcall *AITalkAPI_VersionInfo)(int verbose, _Out_ char *sjis, unsigned int len, _Out_ unsigned int *size);

// Settings

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_ReloadPhraseDic")]
// public static extern AITalkResultCode ReloadPhraseDic(string pathDic);
#define _AITalkAPI_ReloadPhraseDic "_AITalkAPI_ReloadPhraseDic@4"
typedef AITalkResultCode (__stdcall *AITalkAPI_ReloadPhraseDic)(const char *pathDic);

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_ReloadSymbolDic")]
// public static extern AITalkResultCode ReloadSymbolDic(string pathDic);
#define _AITalkAPI_ReloadSymbolDic "_AITalkAPI_ReloadSymbolDic@4"
typedef AITalkResultCode (__stdcall *AITalkAPI_ReloadSymbolDic)(const char *pathDic);

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_ReloadWordDic")]
// public static extern AITalkResultCode ReloadWordDic(string pathDic);
#define _AITalkAPI_ReloadWordDic "_AITalkAPI_ReloadWordDic@4"
typedef AITalkResultCode (__stdcall *AITalkAPI_ReloadWordDic)(const char *pathDic);

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_BLoadWordDic")]
// public static extern AITalkResultCode BLoadWordDic();
#define _AITalkAPI_BLoadWordDic "_AITalkAPI_BLoadWordDic@0"
typedef AITalkResultCode (__stdcall *AITalkAPI_BLoadWordDic)();

// Actions

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_GetParam")]
// public static extern AITalkResultCode GetParam(IntPtr pParam, out uint size);
#define _AITalkAPI_GetParam "_AITalkAPI_GetParam@8"
typedef AITalkResultCode (__stdcall *AITalkAPI_GetParam)(_Inout_opt_ void *pParam, _Out_ unsigned int *size);

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_SetParam")]
// public static extern AITalkResultCode SetParam(IntPtr pParam);
#define _AITalkAPI_SetParam "_AITalkAPI_SetParam@4"
typedef AITalkResultCode (__stdcall *AITalkAPI_SetParam)(const void *pParam);

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_GetData")]
// private static extern AITalkResultCode _GetData(int jobID, short[] rawBuf, uint lenBuf, out uint size);
#define _AITalkAPI_GetData "_AITalkAPI_GetData@16"
typedef AITalkResultCode (__stdcall *AITalkAPI_GetData)(int jobID, _Inout_ short rawBuf[], unsigned int lenBuf, _Out_ unsigned int *size);

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_GetKana")]
// private static extern AITalkResultCode _GetKana(int jobID, StringBuilder textBuf, uint lenBuf, out uint size, out uint pos);
#define _AITalkAPI_GetKana "_AITalkAPI_GetKana@20"
typedef AITalkResultCode (__stdcall *AITalkAPI_GetKana)(int jobID, _Out_ char *textBuf, unsigned int lenBuf, _Out_ unsigned int *size, _Out_ unsigned int *pos);

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_GetJeitaControl")]
// private static extern AITalkResultCode _GetJeitaControl(int jobID, string ctrl);
#define _AITalkAPI_GetJeitaControl "_AITalkAPI_GetJeitaControl@8"
typedef AITalkResultCode (__stdcall *AITalkAPI_GetJeitaControl)(int jobID, const char *ctrl);

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_TextToSpeech")]
// private static extern AITalkResultCode _TextToSpeech(out int jobID, ref AITalk_TJobParam param, string text);
#define _AITalkAPI_TextToSpeech "_AITalkAPI_TextToSpeech@12"
typedef AITalkResultCode (__stdcall *AITalkAPI_TextToSpeech)(_Out_ int *jobID, const AITalk_TJobParam *param, const char *text);

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_TextToKana")]
// private static extern AITalkResultCode _TextToKana(out int jobID, ref AITalk_TJobParam param, string text);
#define _AITalkAPI_TextToKana "_AITalkAPI_TextToKana@12"
typedef AITalkResultCode (__stdcall *AITalkAPI_TextToKana)(_Out_ int *jobID, const AITalk_TJobParam *param, const char *text);

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_CloseSpeech")]
// private static extern AITalkResultCode _CloseSpeech(int jobID, int useEvent = 0);
#define _AITalkAPI_CloseSpeech "_AITalkAPI_CloseSpeech@8"
typedef AITalkResultCode (__stdcall *AITalkAPI_CloseSpeech)(int jobID, _In_opt_ int useEvent);

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_CloseKana")]
// private static extern AITalkResultCode _CloseKana(int jobID, int useEvent = 0);
#define _AITalkAPI_CloseKana "_AITalkAPI_CloseKana@8"
typedef AITalkResultCode (__stdcall *AITalkAPI_CloseKana)(int jobID, _In_opt_ int useEvent);

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_GetStatus")]
// private static extern AITalkResultCode _GetStatus(int jobID, out AITalkStatusCode status);
#define _AITalkAPI_GetStatus "_AITalkAPI_GetStatus@8"
typedef AITalkResultCode (__stdcall *AITalkAPI_GetStatus)(int jobID, _Out_ AITalkStatusCode *status);

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_VoiceClear")]
// private static extern AITalkResultCode _VoiceClear();
#define _AITalkAPI_VoiceClear "_AITalkAPI_VoiceClear@0"
typedef AITalkResultCode (__stdcall *AITalkAPI_VoiceClear)();

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_VoiceLoad")]
// private static extern AITalkResultCode _VoiceLoad(string voiceName);
#define _AITalkAPI_VoiceLoad "_AITalkAPI_VoiceLoad@4"
typedef AITalkResultCode (__stdcall *AITalkAPI_VoiceLoad)(const char *voiceName);

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_LangClear")]
// private static extern AITalkResultCode _LangClear();
#define _AITalkAPI_LangClear "_AITalkAPI_LangClear@0"
typedef AITalkResultCode (__stdcall *AITalkAPI_LangClear)();

// AITalkAPI.cs:
// [DllImport("aitalked.dll", EntryPoint="AITalkAPI_LangLoad")]
// private static extern AITalkResultCode _LangLoad(string dirLang);
#define _AITalkAPI_LangLoad "_AITalkAPI_LangLoad@4"
typedef AITalkResultCode (__stdcall *AITalkAPI_LangLoad)(const char *dirLang);

/* Manager class */

class AITalkAPI
{
public:
  AITalkAPI_Init Init;
  AITalkAPI_BLoadWordDic BLoadWordDic;
  AITalkAPI_CloseKana CloseKana;
  AITalkAPI_CloseSpeech CloseSpeech;
  AITalkAPI_End End;
  AITalkAPI_GetData GetData;
  AITalkAPI_GetJeitaControl GetJeitaControl;
  AITalkAPI_GetParam GetParam;
  AITalkAPI_GetStatus GetStatus;
  AITalkAPI_LangClear LangClear;
  AITalkAPI_LangLoad LangLoad;
  AITalkAPI_SetParam SetParam;
  AITalkAPI_ReloadPhraseDic ReloadPhraseDic;
  AITalkAPI_ReloadSymbolDic ReloadSymbolDic;
  AITalkAPI_ReloadWordDic ReloadWordDic;
  AITalkAPI_TextToKana TextToKana;
  AITalkAPI_TextToSpeech TextToSpeech;
  AITalkAPI_VersionInfo VersionInfo;
  AITalkAPI_VoiceClear VoiceClear;
  AITalkAPI_VoiceLoad VoiceLoad;

  /**
   * @param  h  aitalked.dll module
   *
   * Initialize function pointers in the DLL module.
   */
  bool LoadModule(HMODULE h);

  ///  Return if there are null methods.
  bool IsValid() const
  {
    return Init
      && BLoadWordDic
      && CloseKana
      && CloseSpeech
      && End
      && GetData
      && GetJeitaControl
      && GetParam
      && GetStatus
      && LangClear
      && LangLoad
      && SetParam
      && ReloadPhraseDic
      && ReloadSymbolDic
      && ReloadWordDic
      && TextToKana
      && TextToSpeech
      && VersionInfo
      && VoiceClear
      && VoiceLoad
    ;
  }
};

} // namespace AITalk
