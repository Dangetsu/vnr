#pragma once

// aiaudioapi.h
// 10/12/2014 jichi
#include "aitalk/aiaudiodef.h"
#include "aitalk/_windef.h" // for HMODULE
#include <sal.h> // for _Out_

namespace AITalk
{

/* Exported DLL functions of aitalked.dll */

// Initialization

// AITalkAudio.cs:
// [DllImport("aitalked.dll", EntryPoint="AIAudioAPI_Close")]
// private static extern AIAudioResultCode _Close();
#define _AIAudioAPI_Close "_AIAudioAPI_Close@0"
typedef AIAudioResultCode (__stdcall *AIAudioAPI_Close)();

// AITalkAudio.cs:
// [DllImport("aitalked.dll", EntryPoint="AIAudioAPI_Open")]
// private static extern AIAudioResultCode _Open(ref AIAudio_TConfig config);
#define _AIAudioAPI_Open "_AIAudioAPI_Open@4"
typedef AIAudioResultCode (__stdcall *AIAudioAPI_Open)(const AIAudio_TConfig *config);

// AITalkAudio.cs:
// [DllImport("aitalked.dll", EntryPoint="AIAudioAPI_ClearData")]
// private static extern AIAudioResultCode _ClearData();
#define _AIAudioAPI_ClearData "_AIAudioAPI_ClearData@0"
typedef AIAudioResultCode (__stdcall *AIAudioAPI_ClearData)();

// AITalkAudio.cs:
// [DllImport("aitalked.dll", EntryPoint="AIAudioAPI_PushData")]
// public static extern AIAudioResultCode PushData(byte[] buf, uint len, int stop);
#define _AIAudioAPI_PushData "_AIAudioAPI_PushData@12"
typedef AIAudioResultCode (__stdcall *AIAudioAPI_PushData)(const char *buf, unsigned int len, int stop);

// AITalkAudio.cs:
// [DllImport("aitalked.dll", EntryPoint="AIAudioAPI_PushEvent")]
// public static extern AIAudioResultCode PushEvent(ulong tick, IntPtr userData);
#define _AIAudioAPI_PushEvent "_AIAudioAPI_PushEvent@12"
typedef AIAudioResultCode (__stdcall *AIAudioAPI_PushEvent)(unsigned long tick, const int *userData);

// AITalkAudio.cs:
// [DllImport("aitalked.dll", EntryPoint="AIAudioAPI_Resume")]
// public static extern AIAudioResultCode Resume();
#define _AIAudioAPI_Resume "_AIAudioAPI_Resume@0"
typedef AIAudioResultCode (__stdcall *AIAudioAPI_Resume)();

// AITalkAudio.cs:
// [DllImport("aitalked.dll", EntryPoint="AIAudioAPI_Suspend")]
// public static extern AIAudioResultCode Suspend();
#define _AIAudioAPI_Suspend "_AIAudioAPI_Suspend@0"
typedef AIAudioResultCode (__stdcall *AIAudioAPI_Suspend)();

// AITalkAudio.cs:
// [DllImport("aitalked.dll", EntryPoint="AIAudioAPI_SaveWave")]
// public static extern AIAudioResultCode SaveWave(string path, ref AIAudio_TWaveFormat format, byte[] buf, uint len);
#define _AIAudioAPI_SaveWave "_AIAudioAPI_SaveWave@16"
typedef AIAudioResultCode (__stdcall *AIAudioAPI_SaveWave)(const char *path, const AIAudio_TWaveFormat *format, const char buf[], unsigned int len);

/* Manager class */

class AIAudioAPI
{
public:
  AIAudioAPI_ClearData ClearData;
  AIAudioAPI_Close Close;
  AIAudioAPI_Open Open;
  AIAudioAPI_PushData PushData;
  AIAudioAPI_PushEvent PushEvent;
  AIAudioAPI_Resume Resume;
  AIAudioAPI_SaveWave SaveWave;
  AIAudioAPI_Suspend Suspend;

  /**
   * @param  h  aitalked.dll module
   *
   * Initialize function pointers in the DLL module.
   */
  bool LoadModule(HMODULE h);

  ///  Return if there are null methods.
  bool IsValid() const
  {
    return ClearData
        && Close
        && Open
        && PushData
        && PushEvent
        && Resume
        && SaveWave
        && Suspend
    ;
  }
};

} // namespace AITalk
