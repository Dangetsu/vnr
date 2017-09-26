#pragma once

// aitalkutil.h
// 10/11/2014 jichi
#include "aitalk/aitalkapi.h"
#include "aitalk/aitalksettings.h"
#include "aitalk/aiaudioapi.h"
#include "aitalk/_windef.h"  // for HMODULE
#include <cstddef> // for size_t

namespace AITalk {

// C#: public class AITalkUtil : IDisposable
class AITalkUtil
{
  static AITalkUtil *_instance; // in order to bind "this" for "my" callbacks

  AITalkAPI _talk;
  AIAudioAPI _audio;
  bool _valid;
  bool _synthesizing; // is currently synthesizing text
  char _voicePath[MAX_PATH];    // C:\Program Files\AHS\VOICEROID+\zunko\voice
  char _langPath[MAX_PATH];     // C:\Program Files\AHS\VOICEROID+\zunko\lang
  char _licensePath[MAX_PATH];  // C:\Program Files\AHS\VOICEROID+\zunko\aitalked.lic
  short *_waveBuf;
  size_t _waveBufLength;

  AITalkUtil(const AITalkUtil &) {} // disable copy constructor
public:
  AITalkUtil::AITalkUtil()
    : _valid(false), _synthesizing(false), _waveBuf(nullptr), _waveBufLength(0)
  { _instance = this; }

  ~AITalkUtil()
  {
    Destroy();
    _instance = nullptr;
  }

  /**
   *  @param  h  aitalked.dll module
   *
   *  Create Config and invoke AITalkAPI::Init.
   */
  AITalkResultCode Init(HMODULE h, const AITalkSettings *s = nullptr);

  bool IsValid() const { return _valid; }

  void Destroy()
  {
    if (_valid) {
      _valid = false;
      _audio.Close(); // This function might crash when the audio is active
      _talk.End();
      if (_waveBuf)
        delete _waveBuf;
    }
  }

  AITalkResultCode LoadSettings(const AITalkSettings &val);

private:
  AITalkResultCode InitParam(const AITalkSettings *settings = nullptr);

  // AITalkUtil.cs: public AITalkResultCode GetStatus(int jobID, out AITalkStatusCode status)
  //AITalkResultCode GetStatus(int jobID, _Out_ AITalkStatusCode *status) const
  //{ return _talk.GetStatus(jobID, status); }

  // AITalkUtil.cs: public AITalkResultCode SetParam(ref AITalk_TTtsParam param)
  //AITalkResultCode SetParam(const AITalk_TTtsParam &param)
  //{ return _talk.SetParam(&param); }

  // AITalkUtil.cs: public virtual AITalkResultCode SynthAsync(ref AITalk_TJobParam jobparam, string text)
  AITalkResultCode SynthSync(_Out_ int *jobID, const AITalk_TJobParam &jobparam, const char *text);

  // AITalkUtil.cs: public AITalkResultCode GetParam(ref AITalk_TTtsParam param)
  //AITalkResultCode GetParam(_Out_ AITalk_TTtsParam *param)
  //{
  //  unsigned int num;
  //  return _talk.GetParam(param, &num);
  //}

  // Convert short[] got from talkAPI to byte[] and pass to audio API
  // AITalkUtil.cs: public AIAudioResultCode PushData(short[] wave, int size, int stop)
  AIAudioResultCode PushAudioData(const short wave[], size_t size, bool loop = false);

  //AITalkUtil.cs: public AIAudioResultCode PushEvent(ulong tick, IntPtr userData)
  //AIAudioResultCode PushEvent(unsigned long tick, unsigned long userData)
  AIAudioResultCode PushEvent(unsigned long, unsigned long)
  {
    //return _audio.PushEvent(tick, reinterpret_cast<const int *>(userData));
    // Audio event is disabled, which crashes
    return AIAUDIOERR_SUCCESS;
  }

  // AITalkUtil.cs: protected virtual int MyAITalkProcRawBuf(AITalkEventReasonCode reasonCode, int jobID, ulong tick, IntPtr userData)
  static int __stdcall MyAITalkProcRawBuf(AITalkEventReasonCode reasonCode, int jobID, unsigned long tick, const int *userData);

  // AITalkUtil.cs: pprotected virtual int MyAITalkProcEventTTS(AITalkEventReasonCode reasonCode, int jobID, ulong tick, string name, IntPtr userData)
  static int __stdcall MyAITalkProcEventTTS(AITalkEventReasonCode reasonCode, int jobID, unsigned long tick, const char *name, const int *userData);

  // AITalkUtil.cs: pprotected virtual int MyAITalkProcTextBuf(AITalkEventReasonCode reasonCode, int jobID, IntPtr userData)
  static int __stdcall MyAITalkProcTextBuf(AITalkEventReasonCode reasonCode, int jobID, const int *userData);

  static void __stdcall MyAIAudioProcNotify(unsigned long tick, const int *userData);

public:
  bool IsSynthesizing() const { return _synthesizing; }

  // AITalkUtil::SynthSync: while ((this._playing && (res == AITalkResultCode.AITALKERR_SUCCESS)) && (code != AITalkStatusCode.AITALKSTAT_DONE));
  bool IsPlaying(int jobID) const
  {
    AITalkStatusCode code;
    AITalkResultCode res = _talk.GetStatus(jobID, &code);
    return res == AITALKERR_SUCCESS && code != AITALKSTAT_DONE;
  }

  AIAudioResultCode ClearAudioData() // clear audio
  { return _audio.ClearData(); }

  AITalkResultCode CloseSpeech(int jobID);
  //{
  //  //if (!_synthesizing)
  //  //  return AITALKERR_SUCCESS;

  //  AITalkResultCode code = _talk.CloseSpeech(jobID, 0);
  //  _synthesizing = false;
  //  return code;
  //}

  // AITalkUtil.cs: public AITalkResultCode TextToSpeech(string text)
  AITalkResultCode TextToSpeech(_Out_ int *jobID, const char *text)
  {
    AITalk_TJobParam param;
    param.modeInOut = AITALKIOMODE_PLAIN_TO_WAVE;
    param.userData = nullptr;
    return this->SynthSync(jobID, param, text);
  }

  AIAudioResultCode Suspend() { return _audio.Suspend(); }
  AIAudioResultCode Resume() { return _audio.Resume(); }
};

} // namespace AITalk
