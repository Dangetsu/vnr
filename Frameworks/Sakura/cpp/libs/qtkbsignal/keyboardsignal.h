#ifndef KEYBOARDSIGNAL_H
#define KEYBOARDSIGNAL_H

// keyboardsignal.h
// 9/9/2014 jichi

#include <QtCore/QObject>
#include "sakurakit/skglobal.h"

class KeyboardSignalPrivate;
class KeyboardSignal : public QObject
{
  Q_OBJECT
  Q_DISABLE_COPY(KeyboardSignal)
  SK_EXTEND_CLASS(KeyboardSignal, QObject)
  SK_DECLARE_PRIVATE(KeyboardSignalPrivate)
public:
  explicit KeyboardSignal(QObject *parent = nullptr);
  ~KeyboardSignal();

  bool isEnabled() const; // default false
  void setEnabled(bool t);

  bool isKeyEnabled(quint8 vk) const; // windows VK, default 0
  void setKeyEnabled(quint8 vk, bool value);

  int refreshInterval() const;
  void setRefreshInterval(int value);

  bool isRefreshEnabled() const;
  void setRefreshEnabled(bool value);

public slots:
  void refresh();

signals:
  void pressed(quint8 vk);
  void released(quint8 vk);
};

#endif // KEYBOARDSIGNAL_H
