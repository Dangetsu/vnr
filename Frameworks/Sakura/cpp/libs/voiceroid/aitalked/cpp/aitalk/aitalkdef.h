#pragma once

// aitalkdef.h
// 10/11/2014 jichi
#include "aitalk/aitalkconf.h"

namespace AITalk
{

/* Contants */

// AITalkJobInOut.cs:
// namespace AITalk
// {
//   using System;
//
//   public enum AITalkJobInOut
//   {
//     AITALKIOMODE_AIKANA_TO_JEITA = 0x17,
//     AITALKIOMODE_AIKANA_TO_WAVE = 12,
//     AITALKIOMODE_JEITA_TO_WAVE = 13,
//     AITALKIOMODE_PLAIN_TO_AIKANA = 0x15,
//     AITALKIOMODE_PLAIN_TO_WAVE = 11
//   }
// }
enum AITalkJobInOut : int
{
  AITALKIOMODE_PLAIN_TO_WAVE = 11
  , AITALKIOMODE_AIKANA_TO_WAVE = 12
  , AITALKIOMODE_JEITA_TO_WAVE = 13
  , AITALKIOMODE_PLAIN_TO_AIKANA = 21
  , AITALKIOMODE_AIKANA_TO_JEITA = 23
};

// AITalkStatusCode.cs:
// namespace AITalk
// {
//   using System;
//
//   public enum AITalkStatusCode
//   {
//     AITALKSTAT_DONE = 12,
//     AITALKSTAT_INPROGRESS = 10,
//     AITALKSTAT_STILL_RUNNING = 11,
//     AITALKSTAT_WRONG_STATE = -1
//   }
enum AITalkStatusCode : int
{
  AITALKSTAT_WRONG_STATE = -1
  , AITALKSTAT_INPROGRESS = 10
  , AITALKSTAT_STILL_RUNNING = 11
  , AITALKSTAT_DONE = 12
};

// AITalkResultCode.css:
// namespace AITalk
// {
//   using System;
//
//   public enum AITalkResultCode
//   {
//     AITALKERR_ALREADY_INITIALIZED = 10,
//     AITALKERR_ALREADY_LOADED = 11,
//     AITALKERR_FILE_NOT_FOUND = -1001,
//     AITALKERR_INSUFFICIENT = -20,
//     AITALKERR_INTERNAL_ERROR = -1,
//     AITALKERR_INVALID_ARGUMENT = -3,
//     AITALKERR_INVALID_JOBID = -202,
//     AITALKERR_LICENSE_ABSENT = -100,
//     AITALKERR_LICENSE_EXPIRED = -101,
//     AITALKERR_LICENSE_REJECTED = -102,
//     AITALKERR_NOMORE_DATA = 0xcc,
//     AITALKERR_NOT_INITIALIZED = -10,
//     AITALKERR_NOT_LOADED = -11,
//     AITALKERR_PARTIALLY_REGISTERED = 0x15,
//     AITALKERR_PATH_NOT_FOUND = -1002,
//     AITALKERR_READ_FAULT = -1003,
//     AITALKERR_SUCCESS = 0,
//     AITALKERR_TOO_MANY_JOBS = -201,
//     AITALKERR_UNSUPPORTED = -2,
//     AITALKERR_USERDIC_LOCKED = -1011,
//     AITALKERR_USERDIC_NOENTRY = -1012,
//     AITALKERR_WAIT_TIMEOUT = -4
//   }
// }
enum AITalkResultCode : int
{
  AITALKERR_SUCCESS = 0

  , AITALKERR_ALREADY_INITIALIZED = 10
  , AITALKERR_ALREADY_LOADED = 11
  , AITALKERR_PARTIALLY_REGISTERED = 21
  , AITALKERR_NOMORE_DATA = 204

  , AITALKERR_INTERNAL_ERROR = -1
  , AITALKERR_UNSUPPORTED = -2
  , AITALKERR_INVALID_ARGUMENT = -3
  , AITALKERR_WAIT_TIMEOUT = -4
  , AITALKERR_NOT_INITIALIZED = -10
  , AITALKERR_NOT_LOADED = -11
  , AITALKERR_INSUFFICIENT = -20
  , AITALKERR_TOO_MANY_JOBS = -201
  , AITALKERR_INVALID_JOBID = -202
  , AITALKERR_LICENSE_ABSENT = -100
  , AITALKERR_LICENSE_EXPIRED = -101
  , AITALKERR_LICENSE_REJECTED = -102
  , AITALKERR_FILE_NOT_FOUND = -1001
  , AITALKERR_PATH_NOT_FOUND = -1002
  , AITALKERR_READ_FAULT = -1003
  , AITALKERR_USERDIC_LOCKED = -1011
  , AITALKERR_USERDIC_NOENTRY = -1012
};

// AITalkEventReasonCode.css:
// namespace AITalk
// {
//   using System;
//
//   public enum AITalkEventReasonCode
//   {
//     AITALKEVENT_BOOKMARK = 0x12e,
//     AITALKEVENT_PH_LABEL = 0x12d,
//     AITALKEVENT_RAWBUF_CLOSE = 0xcb,
//     AITALKEVENT_RAWBUF_FLUSH = 0xca,
//     AITALKEVENT_RAWBUF_FULL = 0xc9,
//     AITALKEVENT_TEXTBUF_CLOSE = 0x67,
//     AITALKEVENT_TEXTBUF_FLUSH = 0x66,
//     AITALKEVENT_TEXTBUF_FULL = 0x65
//   }
// }
enum AITalkEventReasonCode : int
{
  AITALKEVENT_TEXTBUF_FULL = 0x65
  , AITALKEVENT_TEXTBUF_FLUSH = 0x66
  , AITALKEVENT_TEXTBUF_CLOSE = 0x67
  , AITALKEVENT_RAWBUF_FULL = 0xc9
  , AITALKEVENT_RAWBUF_FLUSH = 0xca
  , AITALKEVENT_RAWBUF_CLOSE = 0xcb
  , AITALKEVENT_PH_LABEL = 0x12d
  , AITALKEVENT_BOOKMARK = 0x12e
};

/* Function pointers */

// AITalkProcTextBuf.css:
// namespace AITalk
// {
//   using System;
//   using System.Runtime.CompilerServices;
//
//   public delegate int AITalkProcTextBuf(AITalkEventReasonCode reasonCode, int jobID, IntPtr userData);
// }
typedef int (__stdcall *AITalkProcTextBuf)(AITalkEventReasonCode reasonCode, int jobID, const int *userData);

// AITalkProcRawBuf.cs:
// namespace AITalk
// {
//   using System;
//   using System.Runtime.CompilerServices;
//
//   public delegate int AITalkProcRawBuf(AITalkEventReasonCode reasonCode, int jobID, ulong tick, IntPtr userData);
// }
typedef int (__stdcall *AITalkProcRawBuf)(AITalkEventReasonCode reasonCode, int jobID, unsigned long tick, const int *userData);

// AITalkProcEventTTS.cs:
// namespace AITalk
// {
//   using System;
//   using System.Runtime.CompilerServices;
//
//   public delegate int AITalkProcEventTTS(AITalkEventReasonCode reasonCode, int jobID, ulong tick, string name, IntPtr userData);
// }
typedef int (__stdcall *AITalkProcEventTTS)(AITalkEventReasonCode reasonCode, int jobID, unsigned long tick, const char *name, const int *userData);

/* Structures */

// AITalk_TConfig.css:
// namespace AITalk
// {
//   using System;
//   using System.Runtime.InteropServices;
//
//   [StructLayout(LayoutKind.Sequential)]
//   public struct AITalk_TConfig
//   {
//     public int hzVoiceDB;
//     public string dirVoiceDBS;
//     public uint msecTimeout;
//     public string pathLicense;
//     public string codeAuthSeed;
//     public uint lenAuthSeed;
//   }
// }
struct AITalk_TConfig
{
  int hzVoiceDB;
  const char *dirVoiceDBS;
  unsigned int msecTimeout;
  const char *pathLicense;
  const char *codeAuthSeed;
  unsigned int lenAuthSeed;
};

// AITalk_TJobParam.css:
// namespace AITalk
// {
//   using System;
//   using System.Runtime.InteropServices;
//
//   [StructLayout(LayoutKind.Sequential)]
//   public struct AITalk_TJobParam
//   {
//     public AITalkJobInOut modeInOut;
//     public IntPtr userData;
//   }
// }
struct AITalk_TJobParam
{
  AITalkJobInOut modeInOut;
  int *userData;
};

// AITalk_TTtsParam.css:
// namespace AITalk
// {
//   using System;
//   using System.Runtime.InteropServices;
//
//   [StructLayout(LayoutKind.Sequential)]
//   public struct AITalk_TTtsParam
//   {
//     public const int MAX_VOICENAME_ = 80;
//     public uint size;
//     public AITalkProcTextBuf procTextBuf;
//     public AITalkProcRawBuf procRawBuf;
//     public AITalkProcEventTTS procEventTts;
//     public uint lenTextBufBytes;
//     public uint lenRawBufBytes;
//     public float volume;
//     public int pauseBegin;
//     public int pauseTerm;
//     public string voiceName;
//     public TJeitaParam Jeita;
//     public uint numSpeakers;
//     public int __reserved__;
//     public TSpeakerParam[] Speaker;
//     [StructLayout(LayoutKind.Sequential)]
//     public struct TJeitaParam
//     {
//       public string femaleName;
//       public string maleName;
//       public int pauseMiddle;
//       public int pauseLong;
//       public int pauseSentence;
//       public string control;
//     }
//
//     [StructLayout(LayoutKind.Sequential)]
//     public struct TSpeakerParam
//     {
//       public string voiceName;
//       public float volume;
//       public float speed;
//       public float pitch;
//       public float range;
//       public int pauseMiddle;
//       public int pauseLong;
//       public int pauseSentence;
//     }
//   }
// }
struct AITalk_TTtsParam
{
  // C#: public const int MAX_VOICENAME_ = 80;
  enum { MAX_VOICENAME_ = AITALK_MAX_NAME }; // 80 is used in AITalkMarshal.cs

  struct TJeitaParam
  {
    char femaleName[MAX_VOICENAME_];    // default: ""
    char maleName[MAX_VOICENAME_];      // default ""
    int pauseMiddle;    // default 0
    int pauseLong;      // default 0
    int pauseSentence;  // default 0
    char control[12];   // default ""  the length is used in AITalkMarshal.cs
  };

  struct TSpeakerParam
  {
    char voiceName[MAX_VOICENAME_];
    float volume;
    float speed;
    float pitch;
    float range;
    int pauseMiddle;
    int pauseLong;
    int pauseSentence;
  };

  unsigned int size;                // default 308
  AITalkProcTextBuf procTextBuf;    // default 0
  AITalkProcRawBuf procRawBuf;      // default 0
  AITalkProcEventTTS procEventTts;  // default 0
  unsigned int lenTextBufBytes;     // default 16384
  unsigned int lenRawBufBytes;      // default 176400
  float volume;                     // default 1
  int pauseBegin;                   // default -1
  int pauseTerm;                    // default -1
  char voiceName[MAX_VOICENAME_];   // default empty
  TJeitaParam Jeita;
  unsigned int numSpeakers;         // default 0
  int __reserved__;
  TSpeakerParam *Speaker; // TSpeakerParam[] Speaker;

  size_t TotalSize() const
  { return sizeof(*this) + numSpeakers * sizeof(TSpeakerParam); }
};

} // namespace AITalk
