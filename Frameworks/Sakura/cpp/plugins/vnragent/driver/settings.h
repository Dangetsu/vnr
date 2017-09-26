#pragma once

// settings.h
// 4/1/2014 jichi

#include "sakurakit/skglobal.h"
#include <QtCore/QObject>

class SettingsPrivate;
// Root object for all qobject
class Settings : public QObject
{
  Q_OBJECT
  Q_DISABLE_COPY(Settings)
  SK_EXTEND_CLASS(Settings, QObject)
  SK_DECLARE_PRIVATE(SettingsPrivate)
public:
  static Self *instance();

  explicit Settings(QObject *parent = nullptr);
  ~Settings();

public:
  bool isEmbedDriverNeeded() const;
  bool isWindowDriverNeeded() const;

  bool isEmbeddedTextNeeded() const; // Whether send embedded text; placeholder that always returns true

  bool isWindowTranslationEnabled() const; // Whether translate text
  bool isWindowTranscodingEnabled() const; // Whether fix text encoding
  bool isWindowTextVisible() const; // Whether display text after the translation
  bool isEmbeddedScenarioVisible() const; // Whether disable scenario text
  bool isEmbeddedScenarioTextVisible() const; // Whether display both scenario text and translation
  bool isEmbeddedScenarioTranslationEnabled() const; // Whether translate scenario text
  bool isEmbeddedScenarioTranscodingEnabled() const; // Whether translate scenario text
  bool isEmbeddedNameVisible() const;
  bool isEmbeddedNameTextVisible() const;
  bool isEmbeddedNameTranslationEnabled() const;
  bool isEmbeddedNameTranscodingEnabled() const;
  bool isEmbeddedOtherVisible() const;
  bool isEmbeddedOtherTextVisible() const;
  bool isEmbeddedOtherTranslationEnabled() const;
  bool isEmbeddedOtherTranscodingEnabled() const;

  bool isEmbeddedSpaceAlwaysInserted() const;
  bool isEmbeddedSpaceSmartInserted() const;
  QString embeddedSpacePolicyEncoding() const;

  bool isEmbeddedAllTextsExtracted() const;
  bool isEmbeddedTextEnabled() const;
  //bool isEmbeddedTextCancellableByControl() const;
  int embeddedTranslationWaitTime() const;

  QString embeddedFontFamily() const;
  float embeddedFontScale() const;
  int embeddedFontWeight() const;
  int embeddedFontCharSet() const;
  bool isEmbeddedFontCharSetEnabled() const;

  QString gameEncoding() const;

  int embeddedScenarioWidth() const;

  long scenarioSignature() const;
  long nameSignature() const;

public slots:
  void load(const QString &json);
  void disable();

  void setWindowTranslationEnabled(bool t);
  void setWindowTranscodingEnabled(bool t);
  void setWindowTextVisible(bool t);
  void setEmbeddedScenarioVisible(bool t);
  void setEmbeddedScenarioTextVisible(bool t);
  void setEmbeddedScenarioTranslationEnabled(bool t);
  void setEmbeddedScenarioTranscodingEnabled(bool t);
  void setEmbeddedNameVisible(bool t);
  void setEmbeddedNameTextVisible(bool t);
  void setEmbeddedNameTranslationEnabled(bool t);
  void setEmbeddedNameTranscodingEnabled(bool t);
  void setEmbeddedOtherVisible(bool t);
  void setEmbeddedOtherTextVisible(bool t);
  void setEmbeddedOtherTranslationEnabled(bool t);
  void setEmbeddedOtherTranscodingEnabled(bool t);

  void setEmbeddedSpaceAlwaysInserted(bool t);
  void setEmbeddedSpaceSmartInserted(bool t);
  void setEmbeddedSpacePolicyEncoding(const QString &v);

  void setEmbeddedAllTextsExtracted(bool t);
  void setEmbeddedTextEnabled(bool t);
  //void setEmbeddedTextCancellableByControl(bool t);
  void setEmbeddedTranslationWaitTime(int v);

  void setEmbeddedScenarioWidth(int v);

  void setEmbeddedFontFamily(const QString &v);
  void setEmbeddedFontCharSetEnabled(bool t);
  void setEmbeddedFontCharSet(int v);
  void setEmbeddedFontWeight(int v);
  void setEmbeddedFontScale(float v);

  void setGameEncoding(const QString &v);

  void setScenarioSignature(long v);
  void setNameSignature(long v);

signals:
  void loadFinished(); // emit after load() is invoked

  void windowTranslationEnabledChanged(bool t);
  void windowTranscodingEnabledChanged(bool t);
  void windowTextVisibleChanged(bool t);
  void embeddedScenarioVisibleChanged(bool t);
  void embeddedScenarioTextVisibleChanged(bool t);
  void embeddedScenarioTranslationEnabledChanged(bool t);
  void embeddedScenarioTranscodingEnabledChanged(bool t);
  void embeddedNameVisibleChanged(bool t);
  void embeddedNameTextVisibleChanged(bool t);
  void embeddedNameTranslationEnabledChanged(bool t);
  void embeddedNameTranscodingEnabledChanged(bool t);
  void embeddedOtherVisibleChanged(bool t);
  void embeddedOtherTextVisibleChanged(bool t);
  void embeddedOtherTranslationEnabledChanged(bool t);
  void embeddedOtherTranscodingEnabledChanged(bool t);

  void embeddedScenarioWidthChanged(int v);

  void embeddedSpaceAlwaysInsertedChanged(bool t);
  void embeddedSpaceSmartInsertedChanged(bool t);
  void embeddedSpacePolicyEncodingChanged(QString v);

  void embeddedAllTextsExtractedChanged(bool t);
  void embeddedTextEnabledChanged(bool t);
  //void embeddedTextCancellableByControlChanged(bool t);
  void embeddedTranslationWaitTimeChanged(int v);

  void embeddedFontFamilyChanged(QString v);
  void embeddedFontCharSetChanged(int v);
  void embeddedFontCharSetEnabledChanged(bool t);
  void embeddedFontWeightChanged(int v);
  void embeddedFontScaleChanged(float v);

  void gameEncodingChanged(QString v);
  void scenarioSignatureChanged(long v);
  void nameSignatureChanged(long v);
};

// EOF
