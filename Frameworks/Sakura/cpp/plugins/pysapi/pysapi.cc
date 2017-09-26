// pysapi.cc
// 4/7/2013

#include "pysapi/pysapi.h"
#include "wintts/wintts.h"

/** Private class */

class SapiPlayer_p
{
public:
  wintts_t *tts;
  std::wstring voice; // voice registry path

  SapiPlayer_p(): tts(::wintts_create()) {}
  ~SapiPlayer_p() { ::wintts_destroy(tts); }
};

/** Public class */

// - Construction -

SapiPlayer::SapiPlayer() : d_(new D) {}
SapiPlayer::~SapiPlayer() { delete d_; }

bool SapiPlayer::isValid() const { return d_->tts; }

bool SapiPlayer::setVoice(const std::wstring &registry)
{
  bool ret = false;
  if (d_->voice != registry)
    if (ret = ::wintts_set_voice(d_->tts, registry.c_str()))
      d_->voice = ret;
  return ret;
}

std::wstring SapiPlayer::voice() const { return d_->voice; }
bool SapiPlayer::hasVoice() const { return !d_->voice.empty(); }

// - Actions -

bool SapiPlayer::purge(bool async) const
{ return ::wintts_speak(d_->tts, nullptr, WINTTS_PURGE | (async ? WINTTS_ASYNC : 0)); }

bool SapiPlayer::speak(const std::wstring &text, bool async) const
{ return ::wintts_speak(d_->tts, text.c_str(), async ? WINTTS_ASYNC : WINTTS_DEFAULT); }

// EOF
