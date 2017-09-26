#ifndef MOUSESELECTOR_P_H
#define MOUSESELECTOR_P_H

// mouseselector_p.h
// 8/21/2014 jichi

//#include <QtCore/QObject>
//#include <QtGui/qwindowdefs.h> // for WId
#include <QtGlobal>
#include "sakurakit/skglobal.h"

QT_FORWARD_DECLARE_CLASS(QTimer)

class MouseRubberBand;
class MouseSelector;
class MouseSelectorPrivate //: public QObject
{
  //Q_OBJECT
  //Q_DISABLE_COPY(MouseSelectorPrivate)
  //SK_EXTEND_CLASS(MouseSelectorPrivate, QObject)
  SK_CLASS(MouseSelectorPrivate)
  SK_DISABLE_COPY(MouseSelectorPrivate)
  SK_DECLARE_PUBLIC(MouseSelector)
public:
  explicit MouseSelectorPrivate(Q *q);
  ~MouseSelectorPrivate();

public:
  // For mouse selection
  bool enabled;
  int comboKey; // vk
  //QWidget *parentWidget;
  mutable MouseRubberBand *rb; // dynamic create
  bool refreshEnabled;
  QTimer *refreshTimer;

  void createRubberBand() const;

private:
  // For mouse hook
  bool pressed;
  //unsigned long pressedWid;

  bool onMousePress(int x, int y, void *wid);
  bool onMouseMove(int x, int y, void *wid);
  bool onMouseRelease(int x, int y, void *wid);

  bool isPressAllowed() const;

//private slots:
//  void trigger(int x, int y, int width, int height);
};

#endif // MOUSESELECTOR_P_H
