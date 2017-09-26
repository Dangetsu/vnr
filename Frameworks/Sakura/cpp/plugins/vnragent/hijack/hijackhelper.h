#pragma once
// hijackhelper.h
// 5/7/2014 jichi

#include "sakurakit/skglobal.h"
#include <QtCore/QObject>

class HijackSettings;
class HijackHelperPrivate;
// Root object for all qobject
class HijackHelper : public QObject
{
  Q_OBJECT
  Q_DISABLE_COPY(HijackHelper)
  SK_EXTEND_CLASS(HijackHelper, QObject)
  SK_DECLARE_PRIVATE(HijackHelperPrivate)
public:
  static Self *instance(); // needed by hijack functions
  explicit HijackHelper(QObject *parent = nullptr);
  ~HijackHelper();

  HijackSettings *settings() const;

  void setEncoding(const QString &v);
  void setEncodingEnabled(bool t);

  bool isTranscodingNeeded() const;

  quint8 systemCharSet() const;
};


// EOF
