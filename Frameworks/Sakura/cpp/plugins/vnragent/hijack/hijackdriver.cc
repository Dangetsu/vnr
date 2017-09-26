// hijackdriver.cc
// 5/1/2014 jichi
#include "hijack/hijackdriver.h"
#include "hijack/hijackhelper.h"
#include "hijack/hijackmodule.h"
#include "hijack/hijacksettings.h"
#include <QtCore/QTimer>

#define DEBUG "hijackdriver"
#include "sakurakit/skdebug.h"

/** Private class */

class HijackDriverPrivate
{
  typedef HijackDriver Q;

  enum { RefreshInterval = 5000 }; // interval checking if new module/process is loaded
  QTimer *refreshTimer;
public:
  HijackHelper *helper;

  explicit HijackDriverPrivate(Q *q)
  {
    helper = new HijackHelper(q);

    refreshTimer = new QTimer(q);
    refreshTimer->setSingleShot(false);
    refreshTimer->setInterval(RefreshInterval);
    q->connect(refreshTimer, SIGNAL(timeout()), SLOT(refresh()));

    refreshTimer->start();
  }
};

/** Public class */

HijackDriver::HijackDriver(QObject *parent) : Base(parent), d_(new D(this)) {}
HijackDriver::~HijackDriver() { delete d_; }

// Properties

void HijackDriver::setDeviceContextFontEnabled(bool t)
{
  d_->helper->settings()->deviceContextFontEnabled = t;
  DOUT(t);
}

void HijackDriver::setLocaleEmulationEnabled(bool t)
{
  d_->helper->settings()->localeEmulationEnabled = t;
  DOUT(t);
}

void HijackDriver::setEncoding(const QString &v)
{
  d_->helper->setEncoding(v);
  DOUT(v);
}

void HijackDriver::setFontCharSetEnabled(bool t)
{
  d_->helper->settings()->fontCharSetEnabled = t;
  DOUT(t);
}

void HijackDriver::setFontCharSet(int v)
{
  d_->helper->settings()->fontCharSet = (quint8)v;
  DOUT(v);
}

void HijackDriver::setFontWeight(int v)
{
  d_->helper->settings()->fontWeight = v;
  DOUT(v);
}

void HijackDriver::setFontScale(float v)
{
  d_->helper->settings()->fontScale = v;
  DOUT(v);
}

void HijackDriver::setFontFamily(const QString &v)
{
  d_->helper->settings()->fontFamily = v;
  DOUT(v);
}

// Actions

void HijackDriver::refresh()
{ Hijack::overrideModules(); }

void HijackDriver::unload()
{ Hijack::restoreModules(); }

// EOF
