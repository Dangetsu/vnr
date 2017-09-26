// pywmp.cc
// 10/5/2014

#include "pywmp/pywmp.h"
#include "wmpcli/wmpcli.h"
#include "ccutil/ccmacro.h"

/** Private class */

class WindowsMediaPlayer_p
{
public:
  wmp_player_t *p;
  wmp_controls_t *c;
  wmp_settings_t *s;

  WindowsMediaPlayer_p()
    : p(nullptr), c(nullptr), s(nullptr)
  {
    if (p = wmp_player_create()) {
      c = wmp_player_get_controls(p);
      if (s = wmp_player_get_settings(p))
        wmp_settings_set_errordialogsenabled(s, false);
    }
  }

  ~WindowsMediaPlayer_p()
  {
    if (s)
      wmp_release(s);
    if (c)
      wmp_release(c);
    if (p)
      wmp_release(p);
  }
};

/** Public class */

// - Construction -

WindowsMediaPlayer::WindowsMediaPlayer() : d_(new D) {}
WindowsMediaPlayer::~WindowsMediaPlayer() { delete d_; }

bool WindowsMediaPlayer::isValid() const { return d_->s && d_->c && d_->p; }

std::wstring WindowsMediaPlayer::version() const
{ return d_->p ? wmp_player_get_version(d_->p) : L""; }

// Controls

bool WindowsMediaPlayer::play(const std::wstring &url)
{ return d_->p && wmp_player_set_url(d_->p, url.c_str()); }

bool WindowsMediaPlayer::stop()
{ return d_->p && wmp_controls_stop(d_->c); }

// Settings

int WindowsMediaPlayer::volume() const
{ return d_->s ? wmp_settings_get_volume(d_->s) : 0; }

void WindowsMediaPlayer::setVolume(int v)
{ if (CC_LIKELY(d_->s)) wmp_settings_set_volume(d_->s, v); }

double WindowsMediaPlayer::speed() const
{ return d_->s ? wmp_settings_get_rate(d_->s) : 0; }

void WindowsMediaPlayer::setSpeed(double v)
{ if (CC_LIKELY(d_->s)) wmp_settings_set_rate(d_->s, v); }

// EOF
