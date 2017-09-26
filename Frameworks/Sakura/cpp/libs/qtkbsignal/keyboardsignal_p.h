#ifndef KEYBOARDSIGNAL_P_H
#define KEYBOARDSIGNAL_P_H

// keyboardsignal_p.h
// 9/9/2014 jichi

#include <QtGlobal>
#include "sakurakit/skglobal.h"

QT_FORWARD_DECLARE_CLASS(QTimer)

class KeyboardSignal;
class KeyboardSignalPrivate //: public QObject
{
  //Q_OBJECT
  //Q_DISABLE_COPY(KeyboardSignalPrivate)
  //SK_EXTEND_CLASS(KeyboardSignalPrivate, QObject)
  SK_CLASS(KeyboardSignalPrivate)
  SK_DISABLE_COPY(KeyboardSignalPrivate)
  SK_DECLARE_PUBLIC(KeyboardSignal)
public:
  explicit KeyboardSignalPrivate(Q *q);
  ~KeyboardSignalPrivate();

public:
  // For mouse selection
  bool enabled;
  qint8 keyEnabled[0xff]; // bool

  QWidget *parentWidget;
  bool refreshEnabled;
  QTimer *refreshTimer;

private:
  bool pressed;
  bool onKeyDown(unsigned char vk);
  bool onKeyUp(unsigned char vk);
};

#endif // KEYBOARDSIGNAL_P_H
