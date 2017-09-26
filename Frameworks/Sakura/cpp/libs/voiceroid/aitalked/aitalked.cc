// aitalked.cc
// 10/12/2014 jichi
#include "aitalked/aitalked.h"
#include "aitalk/aitalkutil.h"
#include <windows.h>
#include "cpputil/cppmath.h"

using namespace AITalk;

/** Private class */

class AITalkSynthesizerPrivate
{
public:
  AITalkUtil ai;
  HMODULE h;
  int jobId;
  AITalkSettings settings;

  AITalkSynthesizerPrivate()
    : h(nullptr), jobId(0) {}
};

/** Public class */

AITalkSynthesizer::AITalkSynthesizer(float volume, unsigned int audioBufferSize)
  : d_(new D)
{
  d_->settings.volume = volume;
  d_->settings.audioBufferSize = audioBufferSize;
}

AITalkSynthesizer::~AITalkSynthesizer()
{
  HMODULE h = d_->h;
  delete d_;
  if (h)
    ::FreeLibrary(h);
}

bool AITalkSynthesizer::isValid() const { return d_->ai.IsValid(); }

bool AITalkSynthesizer::init(const std::wstring &path)
{
  if (d_->h)
    ::FreeLibrary(d_->h);
  d_->h = LoadLibraryW(path.c_str());
  if (!d_->h)
    return false;

  return d_->ai.Init(d_->h, &d_->settings) == 0;
}

// Settings

float AITalkSynthesizer::volume() const { return d_->settings.volume; }

void AITalkSynthesizer::setVolume(float v)
{
  if (!cpp_fuzzy_compare(v, d_->settings.volume)) {
    d_->settings.volume = v;
    if (d_->ai.IsValid())
      d_->ai.LoadSettings(d_->settings);
  }
}

// Actions

bool AITalkSynthesizer::pause()
{ return d_->ai.IsValid() && d_->ai.Suspend() == 0; }

bool AITalkSynthesizer::resume()
{ return d_->ai.IsValid() && d_->ai.Resume() == 0; }

void AITalkSynthesizer::stop()
{
  if (d_->ai.IsValid() && d_->ai.IsSynthesizing() && d_->jobId) {
    d_->ai.CloseSpeech(d_->jobId);
    d_->jobId = 0;
    d_->ai.ClearAudioData();
  }
}

bool AITalkSynthesizer::speak(const char *text)
{
  if (!d_->ai.IsValid())
    return false;
  //if (d_->ai.IsSynthesizing() && d_->jobId)
  if (d_->jobId) // always close in the main thread no matter synthesizing or not
    d_->ai.CloseSpeech(d_->jobId);
  d_->jobId = 0;
  return d_->ai.TextToSpeech(&d_->jobId, text) == 0;
}

bool AITalkSynthesizer::isPlaying() const
{ return d_->ai.IsSynthesizing() || d_->jobId && d_->ai.IsPlaying(d_->jobId); }

// EOF
