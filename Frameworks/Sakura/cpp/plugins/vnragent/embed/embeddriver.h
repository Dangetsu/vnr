#pragma once

// embeddriver.h
// 4/26/2014 jichi

#include "sakurakit/skglobal.h"
#include <QtCore/QObject>
#include <QtCore/QString>

class EmbedDriverPrivate;
class EmbedDriver : public QObject
{
  Q_OBJECT
  Q_DISABLE_COPY(EmbedDriver)
  SK_EXTEND_CLASS(EmbedDriver, QObject)
  SK_DECLARE_PRIVATE(EmbedDriverPrivate)

public:
  explicit EmbedDriver(QObject *parent = nullptr);
  ~EmbedDriver();

  bool isDeviceContextFontEnabled() const;
  bool isLocaleEmulationEnabled() const;

signals:
  void textReceived(QString text, qint64 hash, long signature, int role, bool needsTranslation);
  void engineNameChanged(QString name);
public slots:
  void sendEngineName();
  //void updateTranslation(const QString &text, qint64 hash, int role);
  void clearTranslation();

  void setTranslationWaitTime(int v);

  void setEnabled(bool t);
  void setEncoding(const QString &v);
  //void setDetectsControl(bool t);
  void setExtractsAllTexts(bool t);
  void setScenarioVisible(bool t);
  void setScenarioTextVisible(bool t);
  void setScenarioExtractionEnabled(bool t);
  void setScenarioTranscodingEnabled(bool t);
  void setScenarioTranslationEnabled(bool t);
  void setNameVisible(bool t);
  void setNameTextVisible(bool t);
  void setNameExtractionEnabled(bool t);
  void setNameTranscodingEnabled(bool t);
  void setNameTranslationEnabled(bool t);
  void setOtherVisible(bool t);
  void setOtherTextVisible(bool t);
  void setOtherExtractionEnabled(bool t);
  void setOtherTranscodingEnabled(bool t);
  void setOtherTranslationEnabled(bool t);

  void setAlwaysInsertsSpaces(bool t);
  void setSmartInsertsSpaces(bool t);
  void setSpacePolicyEncoding(const QString &v);

  void setScenarioWidth(int v);

  void setScenarioSignature(long v);
  void setNameSignature(long v);

  // Called by engine
public:
  void quit();
  bool load();
  void unload();
  QString engineName() const;
};

// EOF
