#pragma once

// windowdriver.h
// 2/1/2013 jichi

#include "sakurakit/skglobal.h"
#include <QtCore/QObject>

class WindowDriverPrivate;
class WindowDriver : public QObject
{
  Q_OBJECT
  Q_DISABLE_COPY(WindowDriver)
  SK_EXTEND_CLASS(WindowDriver, QObject)
  SK_DECLARE_PRIVATE(WindowDriverPrivate)

public:
  explicit WindowDriver(QObject *parent = nullptr);

signals:
  void translationRequested(QString json); // {long hash : unicode text}
public slots:
  void updateTranslation(const QString &json); // {long hash : unicode translation}
  void clearTranslation();

  void setEnabled(bool t);
  void setTextVisible(bool t);
  void setTranslationEnabled(bool t);
  void setTranscodingEnabled(bool t);
  void setEncoding(const QString &v);
};

// EOF
