// mouseselector.cc
// 8/21/2014 jichi
#include "qtmousesel/mouseselector.h"
#include "qtmousesel/mouseselector_p.h"
#include "qtrubberband/mouserubberband.h"

#ifdef Q_OS_WIN
# include "mousehook/mousehook.h"
# include "winkey/winkey.h"
#else
# error "Windows only"
#endif // Q_OS_WIN

#include <QtCore/QTimer>
#include <boost/bind.hpp>

#define DEBUG "mouseselector"
#include "sakurakit/skdebug.h"

enum { DEFAULT_REFRESH_INTERVAL = 5000 }; // 5 seconds

/** Private class */

// Construction

MouseSelectorPrivate::MouseSelectorPrivate(Q *q)
  : q_(q)
  , enabled(false)
  , comboKey(0)
  //, parentWidget(nullptr)
  , rb(nullptr)
  , refreshEnabled(false)
  , refreshTimer(nullptr)
  , pressed(false)
  //, pressedWid(0)
{
  refreshTimer = new QTimer(q);
  refreshTimer->setSingleShot(false);
  refreshTimer->setInterval(DEFAULT_REFRESH_INTERVAL);
  q_->connect(refreshTimer, SIGNAL(timeout()), SLOT(refresh()));

  ::mousehook_onlbuttondown(boost::bind(&Self::onMousePress, this, _1, _2, _3));
  ::mousehook_onlbuttonup(boost::bind(&Self::onMouseRelease, this, _1, _2, _3));
  ::mousehook_onmove(boost::bind(&Self::onMouseMove, this, _1, _2, _3));
}

MouseSelectorPrivate::~MouseSelectorPrivate()
{
  if (enabled)
    ::mousehook_stop();
  ::mousehook_onmove(mousehook_fun_null);
  ::mousehook_onlbuttondown(mousehook_fun_null);
  ::mousehook_onlbuttonup(mousehook_fun_null);
  if (rb)
    delete rb;
}

void MouseSelectorPrivate::createRubberBand() const // const since rb is mutable
{
  rb = new MouseRubberBand(QRubberBand::Rectangle);
  //rb->setWindowFlags(rb->windowFlags() | Qt::Popup); // needed when parentWidget is not nullptr
  q_->connect(rb, SIGNAL(selected(int,int,int,int)), SIGNAL(selected(int,int,int,int)),
      Qt::QueuedConnection); // use queued connection to leave mouse event loop
}

//void MouseSelectorPrivate::trigger(int x, int y, int width, int height)
//{ q_->emit selected(x, y, width, height, pressedWid); }

// Callbacks

bool MouseSelectorPrivate::isPressAllowed() const
{ return !comboKey || WinKey::isKeyPressed(comboKey); }

bool MouseSelectorPrivate::onMousePress(int x, int y, void *wid)
{
  if (enabled //&& !pressed  // !pressed not checked in case sth is wrong at runtime
              && isPressAllowed()) {
    //pressedWid = reinterpret_cast<WId>(wid);
    pressed = true;
    q_->emit pressed(x, y);
    rb->press(x, y);
    DOUT("pass");
    return true;
  }
  return false;
}

bool MouseSelectorPrivate::onMouseMove(int x, int y, void *wid)
{
  Q_UNUSED(wid);
  if (enabled && pressed)
    rb->move(x, y);
  return false;
}

bool MouseSelectorPrivate::onMouseRelease(int x, int y, void *wid)
{
  Q_UNUSED(wid);
  if (enabled && pressed) {
    pressed = false;
    q_->emit released(x, y);
    rb->move(x, y);
    rb->release();
    DOUT("pass");
    return true;
  }
  return false;
}

/** Public class */

MouseSelector::MouseSelector(QObject *parent) : Base(parent), d_(new D(this)) {}
MouseSelector::~MouseSelector() { delete d_; }

QRubberBand *MouseSelector::rubberBand() const
{
  if (!d_->rb)
    d_->createRubberBand();
  return d_->rb;
}

//QWidget *MouseSelector::parentWidget() const { return d_->parentWidget; }
//void MouseSelector::setParentWidget(QWidget *v)
//{
//  if (d_->parentWidget != v) {
//    d_->parentWidget = v;
//    if (d_->rb)
//      d_->rb->setParent(v);
//  }
//}

int MouseSelector::comboKey() const
{ return d_->comboKey; }

void MouseSelector::setComboKey(int vk)
{ d_->comboKey = vk; }

bool MouseSelector::isEnabled() const
{ return d_->enabled; }

void MouseSelector::setEnabled(bool t)
{
  if (d_->enabled != t) {
    DOUT(t);
    if (t) {
      if (!d_->rb)
        d_->createRubberBand();
      d_->enabled = true;
      ::mousehook_start();
      if (d_->refreshEnabled)
        d_->refreshTimer->start();
    } else {
      ::mousehook_stop();
      d_->enabled = false;
      if (d_->refreshEnabled)
        d_->refreshTimer->stop();
    }
  }
}

int MouseSelector::refreshInterval() const { return d_->refreshTimer->interval(); }
void MouseSelector::setRefreshInterval(int v) { d_->refreshTimer->setInterval(v); }

bool MouseSelector::isRefreshEnabled() const { return d_->refreshEnabled; }
void MouseSelector::setRefreshEnabled(bool t)
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

void MouseSelector::refresh()
{
  if (d_->enabled && !d_->pressed) // no need to refresh when already pressed
    ::mousehook_restart();
}

// EOF
