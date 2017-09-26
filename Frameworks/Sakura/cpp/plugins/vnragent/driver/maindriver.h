#pragma once

// maindriver.h
// 2/1/2013 jichi

#include "sakurakit/skglobal.h"
#include <QtCore/QObject>

class MainDriverPrivate;
// Root object for all qobject
class MainDriver : public QObject
{
  Q_OBJECT
  Q_DISABLE_COPY(MainDriver)
  SK_EXTEND_CLASS(MainDriver, QObject)
  SK_DECLARE_PRIVATE(MainDriverPrivate)
public:
  explicit MainDriver(QObject *parent = nullptr);
  ~MainDriver();

  void quit();
  // Connected with deleteLater through queued signal
  void requestDeleteLater();

signals:
  void deleteLaterRequested();
};

// EOF
