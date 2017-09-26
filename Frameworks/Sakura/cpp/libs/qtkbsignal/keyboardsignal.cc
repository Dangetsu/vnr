// keyboardsignal.cc
// 9/9/2014 jichi
#include "qtkbsignal/keyboardsignal.h"
#include "qtkbsignal/keyboardsignal_p.h"

#ifdef Q_OS_WIN
# include "keyboardhook/keyboardhook.h"
//# include "winkey/winkey.h"
#else
# error "Windows only"
#endif // Q_OS_WIN

#include <QtCore/QTimer>
#include <boost/bind.hpp>

#define DEBUG "keyboardsignal"
#include "sakurakit/skdebug.h"

enum { DEFAULT_REFRESH_INTERVAL = 5000 }; // 5 seconds

/** Private class */

// Construction

KeyboardSignalPrivate::KeyboardSignalPrivate(Q *q)
  : q_(q)
  , enabled(false)
  , refreshEnabled(false)
  , refreshTimer(nullptr)
  , pressed(false)
{
  ::memset(keyEnabled, 0, sizeof(keyEnabled));

  refreshTimer = new QTimer(q);
  refreshTimer->setSingleShot(false);
  refreshTimer->setInterval(DEFAULT_REFRESH_INTERVAL);
  q_->connect(refreshTimer, SIGNAL(timeout()), SLOT(refresh()));

  ::kbhook_onkeydown(boost::bind(&Self::onKeyDown, this, _1));
  ::kbhook_onkeyup(boost::bind(&Self::onKeyUp, this, _1));
}

KeyboardSignalPrivate::~KeyboardSignalPrivate()
{
  if (enabled)
    ::kbhook_stop();
  ::kbhook_onkeydown(kbhook_fun_null);
  ::kbhook_onkeyup(kbhook_fun_null);
}

// Callbacks

bool KeyboardSignalPrivate::onKeyDown(unsigned char vk)
{
  if (enabled && keyEnabled[vk]) { //&& !pressed  // !pressed not checked in case sth is wrong at runtime
    pressed = true;
    q_->emit pressed(vk);
    DOUT("pass");
    return true;
  }
  return false;
}

bool KeyboardSignalPrivate::onKeyUp(unsigned char vk)
{
  if (enabled && pressed && keyEnabled[vk]) {
    pressed = false;
    q_->emit released(vk);
    DOUT("pass");
    return true;
  }
  return false;
}

/** Public class */

KeyboardSignal::KeyboardSignal(QObject *parent) : Base(parent), d_(new D(this)) {}
KeyboardSignal::~KeyboardSignal() { delete d_; }

bool KeyboardSignal::isKeyEnabled(quint8 vk) const
{ return d_->keyEnabled[vk]; }

void KeyboardSignal::setKeyEnabled(quint8 vk, bool value)
{ d_->keyEnabled[vk] = value; }

bool KeyboardSignal::isEnabled() const
{ return d_->enabled; }

void KeyboardSignal::setEnabled(bool t)
{
  if (d_->enabled != t) {
    DOUT(t);
    if (t) {
      d_->enabled = true;
      ::kbhook_start();
      if (d_->refreshEnabled)
        d_->refreshTimer->start();
    } else {
      ::kbhook_stop();
      d_->enabled = false;
      if (d_->refreshEnabled)
        d_->refreshTimer->stop();
    }
  }
}

int KeyboardSignal::refreshInterval() const { return d_->refreshTimer->interval(); }
void KeyboardSignal::setRefreshInterval(int v) { d_->refreshTimer->setInterval(v); }

bool KeyboardSignal::isRefreshEnabled() const { return d_->refreshEnabled; }
void KeyboardSignal::setRefreshEnabled(bool t)
{
  if (d_->refreshEnabled != t) {
    d_->refreshEnabled = t;
    if (d_->enabled) {
      if (t)
        d_->refreshTimer->start();
      else
        d_->refreshTimer->stop();
    }
  }
}

void KeyboardSignal::refresh()
{
  if (d_->enabled && !d_->pressed) // no need to refresh when already pressed
    ::kbhook_restart();
}

// EOF
