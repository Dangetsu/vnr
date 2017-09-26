// aitalkutil.cc
// 10/11/2014 jichi
#include "aitalk/aitalkutil.h"
#include "aitalk/aitalkapi.h"
#include "aitalk/aitalkmarshal.h"
#include "cpputil/cpppath.h"
#include "ccutil/ccmacro.h"
#include <windows.h>
#include <cstring>
//#include <iostream>

using namespace AITalk;

// Static variables
AITalkUtil *AITalk::AITalkUtil::_instance;

// Construction

AITalkResultCode AITalk::AITalkUtil::Init(HMODULE h, const AITalkSettings *settings)
{
  if (!_talk.LoadModule(h) || !_audio.LoadModule(h))
    return AITALKERR_UNSUPPORTED;

  // Initialize talk API

  char dllpath[MAX_PATH];
  if (!::GetModuleFileNameA(h, dllpath, MAX_PATH))
    return AITALKERR_PATH_NOT_FOUND;

  size_t dirlen = ::cpp_wdirlen(dllpath);
  if (dirlen < 1)
    return AITALKERR_PATH_NOT_FOUND;

  ::memcpy(_voicePath, dllpath, dirlen);
  ::strcpy(_voicePath + dirlen, "voice");

  ::memcpy(_langPath, dllpath, dirlen);
  ::strcpy(_langPath + dirlen, "lang");

  ::memcpy(_licensePath, dllpath, dirlen);
  ::strcpy(_licensePath + dirlen, AITALK_CONFIG_LICENSE);

  AITalkResultCode code;
  {
    AITalk_TConfig config;
    config.hzVoiceDB = AITALK_CONFIG_FREQUENCY;
    config.msecTimeout = AITALK_CONFIG_TIMEOUT;
    config.dirVoiceDBS = _voicePath;
    //config.dirVoiceDBS = "C:\\Program Files\\AHS\\VOICEROID+\\zunko\\voice";
    config.pathLicense = _licensePath;
    //config.pathLicense = "C:\\Program Files\\AHS\\VOICEROID+\\zunko\\aitalk.lic";
    config.codeAuthSeed = AITALK_CONFIG_CODEAUTHSEED;
    config.lenAuthSeed = AITALK_CONFIG_LENAUTHSEED;

    code = _talk.Init(&config);
    if (code != AITALKERR_SUCCESS)
      return code;
  }

  // 10/12/2014: This would crash if multiple MeCab/CaboCha dlls are loaded
  // And there are no ways to try-catch the exception
  code = _talk.LangLoad(_langPath);
  if (code != AITALKERR_SUCCESS)
    return code;

  code =_talk.VoiceLoad(AITALK_CONFIG_VOICENAME);
  if (code != AITALKERR_SUCCESS)
    return code;

  // Initialize audio API
  {
    AIAudio_TConfig config;
    //config.procNotify = this->MyAIAudioProcNotify;
    config.procNotify = nullptr; // not used
    config.msecLatency = AIAUDIO_CONFIG_BUFFERLATENCY;
    config.lenBufferBytes = AITALK_CONFIG_FREQUENCY * 2 * AIAUDIO_CONFIG_BUFFERLENGTH;
    config.hzSamplesPerSec = AITALK_CONFIG_FREQUENCY;
    config.formatTag = AIAUDIOTYPE_PCM_16;
    config.__reserved__ = 0;
    AIAudioResultCode code = _audio.Open(&config);
    if (code != AIAUDIOERR_SUCCESS)
      return AITALKERR_INTERNAL_ERROR;
  }

  _valid = true; // _valid so that end/close will be invoked on destruction

  code = InitParam(settings);
  if (code != AITALKERR_SUCCESS)
    return code;

  return AITALKERR_SUCCESS;
}

// APIs wrappers

AIAudioResultCode AITalk::AITalkUtil::PushAudioData(const short wave[], size_t size, bool loop)
{
  if (!_synthesizing)
    return AIAUDIOERR_NO_PLAYING;
  //if (!wave)
  //  return AIAUDIOERR_INVALID_ARGUMENT;
  size_t dstlen = size * 2; // 2 = sizeof(short)
  //char *dst = new char[dstlen];
  //if (dstlen)
  //  ::memcpy(dst, wave, dstlen);
  const char *dst = reinterpret_cast<const char *>(wave);
  AIAudioResultCode code = _audio.PushData(dst, dstlen, loop ? 0 : 1);
  //if (code != AIAudioResultCode.AIAUDIOERR_SUCCESS)
  //  this._playing = false;
  return code;
}

AITalkResultCode AITalk::AITalkUtil::InitParam(const AITalkSettings *settings)
{
  //_talk.ReloadSymbolDic(nullptr);
  //_audio.ClearData();

  size_t num;
  AITalkResultCode code = _talk.GetParam(nullptr, &num);
  if (code != AITALKERR_INSUFFICIENT)
    return AITALKERR_INSUFFICIENT;

  char *data = new char[num];
  ((int *)data)[0] = num;
  //IntPtr ptr = Marshal.AllocCoTaskMem((int) num);
  code = _talk.GetParam(data, &num);
  if (code != AITALKERR_SUCCESS) {
    delete data;
    return code;
  }
  AITalk_TTtsParam param;
  AITalkMarshal::ReadTtsParam(&param, data);
  param.procRawBuf = this->MyAITalkProcRawBuf;
  //param.procTextBuf = this->MyAITalkProcTextBuf;   // TTS Kana is disabled
  //param.procEventTts = this->MyAITalkProcEventTTS; // events are diabled

  // FIXME: Why numSpeakers is null?!
  //if (!param.numSpeakers) {
  //  delete data;
  //  param.numSpeakers = 1;
  //  param.Speaker = new AITalk_TTtsParam::TSpeakerParam[1];
  //  auto sp = param.Speaker[0];
  //  ::strcpy(sp.voiceName, param.voiceName);
  //  sp.volume = 2.0;
  //  sp.speed = 2.0;
  //  sp.pitch = 2.0;
  //  sp.range = 2.0;
  //  sp.pauseMiddle = param.Jeita.pauseMiddle;
  //  sp.pauseLong = param.Jeita.pauseLong;
  //  sp.pauseSentence = param.Jeita.pauseSentence;
  //  data = new char[param.TotalSize()];
  //}

  // Small value would crash for long text
  param.lenRawBufBytes = AITALK_CONFIG_BUFFERLENGTH;

  if (settings) {
    param.volume = settings->volume;
    param.lenRawBufBytes = settings->audioBufferSize ? settings->audioBufferSize : AITALK_CONFIG_BUFFERLENGTH;
  }

  AITalkMarshal::WriteTtsParam(data, param);

  code = _talk.SetParam(data);
  delete data;
  if (code != AITALKERR_SUCCESS)
    return code;

  _waveBufLength = param.lenRawBufBytes / 2; // sizeof(short) == 2
  _waveBuf = new short[_waveBufLength];
  return AITALKERR_SUCCESS;
}

AITalkResultCode AITalk::AITalkUtil::LoadSettings(const AITalkSettings &settings)
{
  size_t num;
  AITalkResultCode code = _talk.GetParam(nullptr, &num);
  if (code != AITALKERR_INSUFFICIENT)
    return AITALKERR_INSUFFICIENT;

  char *data = new char[num];
  ((int *)data)[0] = num;

  code = _talk.GetParam(data, &num);
  if (code != AITALKERR_SUCCESS) {
    delete data;
    return code;
  }

  AITalk_TTtsParam param;
  AITalkMarshal::ReadTtsParam(&param, data);

  param.volume = settings.volume;

  AITalkMarshal::WriteTtsParam(data, param);
  code = _talk.SetParam(data);
  delete data;
  return code;
}

// Speech synthesize

AITalkResultCode AITalk::AITalkUtil::SynthSync(int *jobID, const AITalk_TJobParam &jobparam, const char *text)
{
  if (_synthesizing)
    return AITALKERR_TOO_MANY_JOBS;
  _synthesizing = true;
  _audio.ClearData();

  AITalkResultCode code = _talk.TextToSpeech(jobID, &jobparam, text);
  if (code != AITALKERR_SUCCESS)
    _synthesizing = false;
  return code;
}

// Hooks

void AITalk::AITalkUtil::MyAIAudioProcNotify(unsigned long tick, const int *userData)
{
  CC_UNUSED(tick);
  CC_UNUSED(userData);
}

int AITalk::AITalkUtil::MyAITalkProcEventTTS(AITalkEventReasonCode reasonCode, int jobID, unsigned long tick, const char *name, const int *userData)
{
  CC_UNUSED(jobID);
  CC_UNUSED(name);
  CC_UNUSED(userData);
  switch (reasonCode) {
  case AITALKEVENT_BOOKMARK: _instance->PushEvent(tick, 0); break;
  case AITALKEVENT_PH_LABEL: _instance->PushEvent(tick, 1); break;
  }
  return 0;
}
int AITalk::AITalkUtil::MyAITalkProcTextBuf(AITalkEventReasonCode reasonCode, int jobID, const int *userData)
{
  CC_UNUSED(reasonCode);
  CC_UNUSED(jobID);
  CC_UNUSED(userData);
  //uint size = 0;
  //uint pos = 0;
  //string str = "";
  //if ((reasonCode == AITalkEventReasonCode.AITALKEVENT_TEXTBUF_FLUSH) || (reasonCode == AITalkEventReasonCode.AITALKEVENT_TEXTBUF_FULL))
  //{
  //  AITalkResultCode code = AITalkAPI.GetKana(jobID, this._kanaBuf, (uint) this._kanaBuf.Capacity, out size, out pos);
  //  this.OnWriteLog(string.Concat(new object[] { "[AITalkAPI_GetKana] ", code, " : ", size }));
  //  str = this._kanaBuf.ToString();
  //}
  return 0;
}

AITalkResultCode AITalk::AITalkUtil::CloseSpeech(int jobID)
{
  //if (!_synthesizing)
  //  return AITALKERR_SUCCESS;
  AITalkResultCode code = _talk.CloseSpeech(jobID, 0);
  _synthesizing = false;
  return code;
}

int AITalk::AITalkUtil::MyAITalkProcRawBuf(AITalkEventReasonCode reasonCode, int jobID, unsigned long tick, const int *userData)
{
  CC_UNUSED(userData);
  if (!_instance || !_instance->_synthesizing)
    return 0;
  size_t size = 0;
  switch (reasonCode) {
  case AITALKEVENT_RAWBUF_FLUSH:
  case AITALKEVENT_RAWBUF_FULL:
    if (AITALKERR_SUCCESS == _instance->_talk.GetData(jobID, _instance->_waveBuf, _instance->_waveBufLength, &size) && size > 0) {
      if (reasonCode == AITALKEVENT_RAWBUF_FLUSH)
        _instance->PushEvent(tick, 2);
      _instance->PushAudioData(_instance->_waveBuf, size);
      //if (reasonCode == AITALKEVENT_RAWBUF_FLUSH) // && _instance->_synthesizing)
      //  _instance->CloseSpeech(jobID);
      //::Sleep(1000);
      //_instance->CloseSpeech(jobID);
    }
    break;
  //case AITALKEVENT_RAWBUF_CLOSE: // not reachable
  //  _instance->PushEvent(tick, 3);
  //  _instance->PushAudioData(nullptr, 0);
  //  _instance->CloseSpeech(jobID);
  //  break;
  }
  _instance->CloseSpeech(jobID);
  return 0;
}

// EOF
