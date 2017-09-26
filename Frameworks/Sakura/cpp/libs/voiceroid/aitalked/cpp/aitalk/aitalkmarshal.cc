// aitalkmarshal.cc
// 10/11/2014 jichi
#include "aitalk/aitalkmarshal.h"
#include "aitalk/aitalkconf.h"
#include "cpputil/cppmarshal.h"

const void *AITalk::AITalkMarshal::ReadTtsParam(_Out_ AITalk_TTtsParam *param, const void *data)
{
#define get(type, ...) \
    (p = ::cpp_marshal_get##type(p, __VA_ARGS__))
  const char *p = reinterpret_cast<const char *>(data);

  enum { maxlen = AITALK_MAX_NAME };

  get(uint, &param->size);
  get(ptr, &param->procTextBuf);
  get(ptr, &param->procRawBuf);
  get(ptr, &param->procEventTts);
  get(uint, &param->lenTextBufBytes);
  get(uint, &param->lenRawBufBytes);
  get(float, &param->volume);
  get(int, &param->pauseBegin);
  get(int, &param->pauseTerm);
  get(nstr, param->voiceName, maxlen);
  get(nstr, param->Jeita.femaleName, maxlen);
  get(nstr, param->Jeita.maleName, maxlen);
  get(int, &param->Jeita.pauseMiddle);
  get(int, &param->Jeita.pauseLong);
  get(int, &param->Jeita.pauseSentence);
  get(nstr, param->Jeita.control, 12);
  get(uint, &param->numSpeakers);
  get(int, &param->__reserved__);

  if (param->numSpeakers <= 0)
    param->Speaker = nullptr;
  else {
    auto sp = param->Speaker = new AITalk_TTtsParam::TSpeakerParam[param->numSpeakers];
    for (size_t i = 0; i < param->numSpeakers; i++) {
      get(nstr, sp[i].voiceName, AITALK_MAX_NAME);
      get(float, &sp[i].volume);
      get(float, &sp[i].speed);
      get(float, &sp[i].pitch);
      get(float, &sp[i].range);
      get(int, &sp[i].pauseMiddle);
      get(int, &sp[i].pauseLong);
      get(int, &sp[i].pauseSentence);
    }
  }
  return p;
#undef get
}

void *AITalk::AITalkMarshal::WriteTtsParam(_Out_ void *data, const AITalk_TTtsParam &param)
{
#define put(type, ...) \
    (p = ::cpp_marshal_put##type(p, __VA_ARGS__))
  char *p = reinterpret_cast<char *>(data);

  put(uint, param.size);
  put(ptr, param.procTextBuf);
  put(ptr, param.procRawBuf);
  put(ptr, param.procEventTts);
  put(uint32, param.lenTextBufBytes);
  put(uint32, param.lenRawBufBytes);
  put(float, param.volume);
  put(int, param.pauseBegin);
  put(int, param.pauseTerm);
  put(str, param.voiceName);
  put(str, param.Jeita.femaleName);
  put(str, param.Jeita.maleName);
  put(int, param.Jeita.pauseMiddle);
  put(int, param.Jeita.pauseLong);
  put(int, param.Jeita.pauseSentence);
  put(str, param.Jeita.control);
  put(uint, param.numSpeakers);
  put(int, param.__reserved__);
  for (size_t i = 0; i < param.numSpeakers; i++) {
    put(str, param.Speaker[i].voiceName);
    put(float, param.Speaker[i].volume);
    put(float, param.Speaker[i].speed);
    put(float, param.Speaker[i].pitch);
    put(float, param.Speaker[i].range);
    put(int, param.Speaker[i].pauseMiddle);
    put(int, param.Speaker[i].pauseLong);
    put(int, param.Speaker[i].pauseSentence);
  }

#undef put
  return p;
}

// EOF
