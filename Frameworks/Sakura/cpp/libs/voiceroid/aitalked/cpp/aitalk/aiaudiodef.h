#pragma once

// aiaudiodef.h
// 10/12/2014 jichi
#include "aitalk/aitalkconf.h"

namespace AITalk
{

/* Constants */

// AIAudioFormatType.cs:
// namespace AITalk
// {
//   using System;
//
//   public enum AIAudioFormatType
//   {
//     AIAUDIOTYPE_ALAW_8 = 6,
//     AIAUDIOTYPE_MULAW_8 = 7,
//     AIAUDIOTYPE_PCM_16 = 1
//   }
// }
enum AIAudioFormatType
{
  AIAUDIOTYPE_PCM_16 = 1
  , AIAUDIOTYPE_ALAW_8 = 6
  , AIAUDIOTYPE_MULAW_8 = 7
};

// AIAudioResultCode.cs:
// namespace AITalk
// {
//   using System;
//
//   public enum AIAudioResultCode
//   {
//     AIAUDIOERR_ALREADY_OPENED = 11,
//     AIAUDIOERR_DEVICE_INVALIDATED = -21,
//     AIAUDIOERR_INTERNAL_ERROR = -1,
//     AIAUDIOERR_INVALID_ARGUMENT = -3,
//     AIAUDIOERR_INVALID_CALL = -101,
//     AIAUDIOERR_INVALID_EVENT_ORDINAL = -102,
//     AIAUDIOERR_NO_AUDIO_HARDWARE = -20,
//     AIAUDIOERR_NO_NOTIFICATION_CALLBACK = 0x67,
//     AIAUDIOERR_NO_PLAYING = 0x6f,
//     AIAUDIOERR_NOT_INITIALIZED = -10,
//     AIAUDIOERR_NOT_OPENED = -11,
//     AIAUDIOERR_OUT_OF_MEMORY = -100,
//     AIAUDIOERR_SUCCESS = 0,
//     AIAUDIOERR_UNSUPPORTED = -2,
//     AIAUDIOERR_WAIT_TIMEOUT = -4,
//     AIAUDIOERR_WRITE_FAULT = -201
//   }
// }
enum AIAudioResultCode
{
  AIAUDIOERR_SUCCESS = 0

  , AIAUDIOERR_ALREADY_OPENED = 11
  , AIAUDIOERR_NO_NOTIFICATION_CALLBACK = 103
  , AIAUDIOERR_NO_PLAYING = 111

  , AIAUDIOERR_INTERNAL_ERROR = -1
  , AIAUDIOERR_UNSUPPORTED = -2
  , AIAUDIOERR_INVALID_ARGUMENT = -3
  , AIAUDIOERR_WAIT_TIMEOUT = -4
  , AIAUDIOERR_NOT_INITIALIZED = -10
  , AIAUDIOERR_NOT_OPENED = -11
  , AIAUDIOERR_NO_AUDIO_HARDWARE = -20
  , AIAUDIOERR_DEVICE_INVALIDATED = -21
  , AIAUDIOERR_OUT_OF_MEMORY = -100
  , AIAUDIOERR_INVALID_CALL = -101
  , AIAUDIOERR_INVALID_EVENT_ORDINAL = -102
  , AIAUDIOERR_WRITE_FAULT = -201
};

/* Function pointers */

// AIAudioProcNotify.cs:
// namespace AITalk
// {
//   using System;
//   using System.Runtime.CompilerServices;
//
//   public delegate void AIAudioProcNotify(ulong tick, IntPtr userData);
// }
typedef void (__stdcall *AIAudioProcNotify)(unsigned long tick, const int *userData);

/* Structures */

// AIAudio_TConfig.cs:
// namespace AITalk
// {
//   using System;
//   using System.Runtime.InteropServices;
//
//   [StructLayout(LayoutKind.Sequential)]
//   public struct AIAudio_TConfig
//   {
//     public AIAudioProcNotify procNotify;
//     public uint msecLatency;
//     public uint lenBufferBytes;
//     public int hzSamplesPerSec;
//     public AIAudioFormatType formatTag;
//     public int __reserved__;
//   }
// }

struct AIAudio_TConfig
{
  AIAudioProcNotify procNotify;
  unsigned int msecLatency;
  unsigned int lenBufferBytes;
  int hzSamplesPerSec;
  AIAudioFormatType formatTag;
  int __reserved__;
};

// AIAudio_TWaveFormat.cs:
// namespace AITalk
// {
//   using System;
//   using System.Runtime.InteropServices;
//
//   [StructLayout(LayoutKind.Sequential)]
//   public struct AIAudio_TWaveFormat
//   {
//     public int header;
//     public int hzSamplesPerSec;
//     public AIAudioFormatType formatTag;
//   }
// }
struct AIAudio_TWaveFormat
{
  int header;
  int hzSamplesPerSec;
  AIAudioFormatType formatTag;
};

} // namespace AITalk
