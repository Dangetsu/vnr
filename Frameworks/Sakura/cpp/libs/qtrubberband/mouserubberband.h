#ifndef MOUSERUBBERBAND_H
#define MOUSERUBBERBAND_H

// mouserubberband.h
// 8/21/2014 jichi

#include "sakurakit/skglobal.h"
#include <QtGui/QRubberBand>

class MouseRubberBandPrivate;
class MouseRubberBand : public QRubberBand
{
  Q_OBJECT
  Q_DISABLE_COPY(MouseRubberBand)
  SK_EXTEND_CLASS(MouseRubberBand, QRubberBand)
  SK_DECLARE_PRIVATE(MouseRubberBandPrivate)
public:
  explicit MouseRubberBand(Shape s, QWidget *p = nullptr);
  ~MouseRubberBand();

  bool isPressed() const;
  bool isEmpty() const { return size().isEmpty(); }

  void press(int x, int y);
  void move(int x, int y);
  void release();
  void cancel();

signals:
  void selected(int x, int y, int width, int height);
};

#endif // MOUSERUBBERBAND_H
