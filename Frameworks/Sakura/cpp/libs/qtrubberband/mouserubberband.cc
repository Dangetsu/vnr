// mouserubberband.cc
// 8/21/2014 jichi
#include "qtrubberband/mouserubberband.h"
#include <QtGui/QApplication>

//#define DEBUG "mouserubberband"
#include "sakurakit/skdebug.h"

/** Private class */

class MouseRubberBandPrivate
{
public:
  bool pressed;
  int x, y;

  MouseRubberBandPrivate()
    : pressed(false), x(0), y(0) {} // x,y are not initialized
};

/** Public class */

MouseRubberBand::MouseRubberBand(Shape s, QWidget *p)
  : Base(s, p), d_(new D) {}

MouseRubberBand::~MouseRubberBand() { delete d_; }

bool MouseRubberBand::isPressed() const { return d_->pressed; }

void MouseRubberBand::press(int x, int y)
{
  DOUT("enter");
  setGeometry(x, y, 0, 0);
  d_->x = x;
  d_->y = y;
  d_->pressed = true;
  QApplication::setOverrideCursor(Qt::CrossCursor);
  show();
  DOUT("leave");
}

void MouseRubberBand::move(int x, int y)
{
  if (d_->pressed) {
    int x1 = qMin(x, d_->x),
        x2 = qMax(x, d_->x),
        y1 = qMin(y, d_->y),
        y2 = qMax(y, d_->y);
    setGeometry(x1, y1, x2 - x1, y2 - y1);
  }
}

void MouseRubberBand::release()
{
  DOUT("enter");
  cancel();
  QRect r = geometry();
  if (!r.isEmpty())
    emit selected(r.x(), r.y(), r.width(), r.height());
  DOUT("leave");
}

void MouseRubberBand::cancel()
{
  hide();
  if (QApplication::overrideCursor())
    QApplication::restoreOverrideCursor();
  d_->pressed = false;
}

// EOF
