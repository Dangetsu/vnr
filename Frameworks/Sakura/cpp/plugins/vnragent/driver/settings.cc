// settings.cc
// 5/1/2014 jichi

#include "driver/settings.h"

#define DEBUG "settings"
#include "sakurakit/skdebug.h"

/** Private class */

class SettingsPrivate
{
public:
  bool windowTranslationEnabled
     , windowTranscodingEnabled
     , windowTextVisible
     , embeddedScenarioVisible
     , embeddedScenarioTextVisible
     , embeddedScenarioTranslationEnabled
     , embeddedScenarioTranscodingEnabled
     , embeddedNameVisible
     , embeddedNameTextVisible
     , embeddedNameTranslationEnabled
     , embeddedNameTranscodingEnabled
     , embeddedOtherVisible
     , embeddedOtherTextVisible
     , embeddedOtherTranslationEnabled
     , embeddedOtherTranscodingEnabled
     , embeddedSpaceAlwaysInserted
     , embeddedSpaceSmartInserted
     , embeddedTextEnabled
     //, embeddedTextCancellableByControl
     , embeddedAllTextsExtracted
     ;

  bool embeddedFontCharSetEnabled;
  int embeddedFontCharSet;

  int embeddedFontWeight;
  float embeddedFontScale;

  QString embeddedFontFamily;
  QString embeddedSpacePolicyEncoding;
  QString gameEncoding;

  int embeddedTranslationWaitTime;

  int embeddedScenarioWidth;

  long scenarioSignature,
       nameSignature;

  SettingsPrivate()
     : windowTranslationEnabled(false)
     , windowTranscodingEnabled(false)
     , windowTextVisible(false)
     , embeddedScenarioVisible(false)
     , embeddedScenarioTextVisible(false)
     , embeddedScenarioTranslationEnabled(false)
     , embeddedScenarioTranscodingEnabled(false)
     , embeddedNameVisible(false)
     , embeddedNameTextVisible(false)
     , embeddedNameTranslationEnabled(false)
     , embeddedNameTranscodingEnabled(false)
     , embeddedOtherVisible(false)
     , embeddedOtherTextVisible(false)
     , embeddedOtherTranslationEnabled(false)
     , embeddedOtherTranscodingEnabled(false)
     , embeddedSpaceAlwaysInserted(false)
     , embeddedSpaceSmartInserted(false)
     , embeddedTextEnabled(false)
     //, embeddedTextCancellableByControl(false)
     , embeddedAllTextsExtracted(false)
     , embeddedFontCharSetEnabled(false)
     , embeddedFontCharSet(0)
     , embeddedFontWeight(0)
     , embeddedFontScale(0)
     , gameEncoding("shift-jis")
     , embeddedTranslationWaitTime(1000) // 1 second
     , embeddedScenarioWidth(0)
     , scenarioSignature(0)
     , nameSignature(0)
  {}
};

/** Public class */

static Settings *instance_;
Settings *Settings::instance() { return ::instance_; }

Settings::Settings(QObject *parent)
  : Base(parent), d_(new D)
{
  instance_ = this;
}

Settings::~Settings()
{
  instance_ = nullptr;
  delete d_;
}

#define DEFINE_PROPERTY(property, getter, setter, rettype, argtype) \
  rettype Settings::getter() const \
  { return d_->property; } \
  void Settings::setter(argtype value)  \
  { if (d_->property != value) { d_->property = value; emit property##Changed(value); } }

#define DEFINE_BOOL_PROPERTY(property, getter, setter)      DEFINE_PROPERTY(property, getter, setter, bool, bool)
#define DEFINE_INT_PROPERTY(property, getter, setter)       DEFINE_PROPERTY(property, getter, setter, int, int)
#define DEFINE_LONG_PROPERTY(property, getter, setter)      DEFINE_PROPERTY(property, getter, setter, long, long)
#define DEFINE_FLOAT_PROPERTY(property, getter, setter)     DEFINE_PROPERTY(property, getter, setter, float, float)
#define DEFINE_STRING_PROPERTY(property, getter, setter)    DEFINE_PROPERTY(property, getter, setter, QString, const QString &)

DEFINE_BOOL_PROPERTY(windowTranslationEnabled, isWindowTranslationEnabled, setWindowTranslationEnabled)
DEFINE_BOOL_PROPERTY(windowTranscodingEnabled, isWindowTranscodingEnabled, setWindowTranscodingEnabled)
DEFINE_BOOL_PROPERTY(windowTextVisible, isWindowTextVisible, setWindowTextVisible)
DEFINE_BOOL_PROPERTY(embeddedScenarioVisible, isEmbeddedScenarioVisible, setEmbeddedScenarioVisible)
DEFINE_BOOL_PROPERTY(embeddedScenarioTextVisible, isEmbeddedScenarioTextVisible, setEmbeddedScenarioTextVisible)
DEFINE_BOOL_PROPERTY(embeddedScenarioTranslationEnabled, isEmbeddedScenarioTranslationEnabled, setEmbeddedScenarioTranslationEnabled)
DEFINE_BOOL_PROPERTY(embeddedScenarioTranscodingEnabled, isEmbeddedScenarioTranscodingEnabled, setEmbeddedScenarioTranscodingEnabled)
DEFINE_BOOL_PROPERTY(embeddedNameVisible, isEmbeddedNameVisible, setEmbeddedNameVisible)
DEFINE_BOOL_PROPERTY(embeddedNameTextVisible, isEmbeddedNameTextVisible, setEmbeddedNameTextVisible)
DEFINE_BOOL_PROPERTY(embeddedNameTranslationEnabled, isEmbeddedNameTranslationEnabled, setEmbeddedNameTranslationEnabled)
DEFINE_BOOL_PROPERTY(embeddedNameTranscodingEnabled, isEmbeddedNameTranscodingEnabled, setEmbeddedNameTranscodingEnabled)
DEFINE_BOOL_PROPERTY(embeddedOtherVisible, isEmbeddedOtherVisible, setEmbeddedOtherVisible)
DEFINE_BOOL_PROPERTY(embeddedOtherTextVisible, isEmbeddedOtherTextVisible, setEmbeddedOtherTextVisible)
DEFINE_BOOL_PROPERTY(embeddedOtherTranslationEnabled, isEmbeddedOtherTranslationEnabled, setEmbeddedOtherTranslationEnabled)
DEFINE_BOOL_PROPERTY(embeddedOtherTranscodingEnabled, isEmbeddedOtherTranscodingEnabled, setEmbeddedOtherTranscodingEnabled)

DEFINE_BOOL_PROPERTY(embeddedSpaceAlwaysInserted, isEmbeddedSpaceAlwaysInserted, setEmbeddedSpaceAlwaysInserted)
DEFINE_BOOL_PROPERTY(embeddedSpaceSmartInserted, isEmbeddedSpaceSmartInserted, setEmbeddedSpaceSmartInserted)
DEFINE_STRING_PROPERTY(embeddedSpacePolicyEncoding, embeddedSpacePolicyEncoding, setEmbeddedSpacePolicyEncoding)

DEFINE_BOOL_PROPERTY(embeddedTextEnabled, isEmbeddedTextEnabled, setEmbeddedTextEnabled)
//DEFINE_BOOL_PROPERTY(embeddedTextCancellableByControl, isEmbeddedTextCancellableByControl, setEmbeddedTextCancellableByControl)
DEFINE_BOOL_PROPERTY(embeddedAllTextsExtracted, isEmbeddedAllTextsExtracted, setEmbeddedAllTextsExtracted)

DEFINE_INT_PROPERTY(embeddedTranslationWaitTime, embeddedTranslationWaitTime, setEmbeddedTranslationWaitTime)

DEFINE_INT_PROPERTY(embeddedScenarioWidth, embeddedScenarioWidth, setEmbeddedScenarioWidth)

DEFINE_STRING_PROPERTY(embeddedFontFamily, embeddedFontFamily, setEmbeddedFontFamily)
DEFINE_BOOL_PROPERTY(embeddedFontCharSetEnabled, isEmbeddedFontCharSetEnabled, setEmbeddedFontCharSetEnabled)
DEFINE_INT_PROPERTY(embeddedFontCharSet, embeddedFontCharSet, setEmbeddedFontCharSet)

DEFINE_INT_PROPERTY(embeddedFontWeight, embeddedFontWeight, setEmbeddedFontWeight)
DEFINE_FLOAT_PROPERTY(embeddedFontScale, embeddedFontScale, setEmbeddedFontScale)

DEFINE_STRING_PROPERTY(gameEncoding, gameEncoding, setGameEncoding)

DEFINE_LONG_PROPERTY(scenarioSignature, scenarioSignature, setScenarioSignature)
DEFINE_LONG_PROPERTY(nameSignature, nameSignature, setNameSignature)

// Groupped settings

void Settings::disable()
{
  setWindowTranslationEnabled(false);
  setWindowTextVisible(false);

  setEmbeddedTextEnabled(false);
}

bool Settings::isWindowDriverNeeded() const
{ return isWindowTranslationEnabled() || isWindowTranscodingEnabled(); }

bool Settings::isEmbeddedTextNeeded() const { return true; } // placeholder

bool Settings::isEmbedDriverNeeded() const
{
  return true; // always embedding text
  //return isEmbeddedTextNeeded()
  //    || isEmbeddedScenarioTranslationEnabled() || !isEmbeddedScenarioVisible()
  //    || isEmbeddedNameTranslationEnabled() || !isEmbeddedNameVisible()
  //    || isEmbeddedOtherTranslationEnabled() || !isEmbeddedOtherVisible();
}

// Marshal

#include "QxtCore/QxtJSON"
#include <QtCore/QVariantMap>
#include "util/msghandler.h"

void Settings::load(const QString &json)
{
  enum {
    H_debug = 6994359 // "debug"
    , H_gameEncoding = 156622791
    , H_embeddedFontFamily = 112965145
    , H_embeddedFontCharSet = 235985668
    , H_embeddedFontCharSetEnabled = 173862964
    , H_embeddedFontScale = 25063557
    , H_embeddedFontWeight = 128219092
    , H_embeddedScenarioWidth = 28091752
    , H_embeddedTranslationWaitTime = 245002357
    , H_embeddedTextEnabled = 261153908
    //, H_embeddedTextCancellableByControl = 96153884
    , H_embeddedAllTextsExtracted = 227821172
    , H_scenarioSignature = 246832709
    , H_nameSignature = 122678949

    , H_windowTranslationEnabled = 79059828
    , H_windowTranscodingEnabled = 219567700
    , H_windowTextVisibleChange = 23360709
    , H_embeddedScenarioVisible = 207043173
    , H_embeddedScenarioTextVisible = 241097605
    , H_embeddedScenarioTranslationEnabled = 132391348
    , H_embeddedScenarioTranscodingEnabled = 105135476
    , H_embeddedNameVisible = 180590501
    , H_embeddedNameTextVisible = 60027589
    , H_embeddedNameTranslationEnabled = 239147220
    , H_embeddedNameTranscodingEnabled = 266409492
    , H_embeddedOtherVisible = 32685349
    , H_embeddedOtherTextVisible = 151359621
    , H_embeddedOtherTranslationEnabled = 9290068
    , H_embeddedOtherTranscodingEnabled = 19782804
    , H_embeddedSpaceAlwaysInserted = 241397364
    , H_embeddedSpaceSmartInserted = 187266164
    , H_embeddedSpacePolicyEncoding = 213320263
  };

  QVariant data = QxtJSON::parse(json);
  if (data.isNull())
    return;
  QVariantMap map = data.toMap();
  if (map.isEmpty())
    return;

  for (auto it = map.constBegin(); it != map.constEnd(); ++it) {
    QString value = it.value().toString();
    bool bValue = value == "true";
    switch (qHash(it.key())) {
    case H_windowTranslationEnabled: setWindowTranslationEnabled(bValue); break;
    case H_windowTranscodingEnabled: setWindowTranscodingEnabled(bValue); break;
    case H_windowTextVisibleChange: setWindowTextVisible(bValue); break;
    case H_embeddedScenarioVisible: setEmbeddedScenarioVisible(bValue); break;
    case H_embeddedScenarioTextVisible: setEmbeddedScenarioTextVisible(bValue); break;
    case H_embeddedScenarioTranslationEnabled: setEmbeddedScenarioTranslationEnabled(bValue); break;
    case H_embeddedScenarioTranscodingEnabled: setEmbeddedScenarioTranscodingEnabled(bValue); break;
    case H_embeddedNameVisible: setEmbeddedNameVisible(bValue); break;
    case H_embeddedNameTextVisible: setEmbeddedNameTextVisible(bValue); break;
    case H_embeddedNameTranslationEnabled: setEmbeddedNameTranslationEnabled(bValue); break;
    case H_embeddedNameTranscodingEnabled: setEmbeddedNameTranscodingEnabled(bValue); break;
    case H_embeddedOtherVisible: setEmbeddedOtherVisible(bValue); break;
    case H_embeddedOtherTextVisible: setEmbeddedOtherTextVisible(bValue); break;
    case H_embeddedOtherTranslationEnabled: setEmbeddedOtherTranslationEnabled(bValue); break;
    case H_embeddedOtherTranscodingEnabled: setEmbeddedOtherTranscodingEnabled(bValue); break;

    case H_embeddedSpaceAlwaysInserted: setEmbeddedSpaceAlwaysInserted(bValue); break;
    case H_embeddedSpaceSmartInserted: setEmbeddedSpaceSmartInserted(bValue); break;
    case H_embeddedSpacePolicyEncoding: setEmbeddedSpacePolicyEncoding(value); break;

    case H_embeddedTextEnabled: setEmbeddedTextEnabled(bValue); break;
    //case H_embeddedTextCancellableByControl: setEmbeddedTextCancellableByControl(bValue); break;
    case H_embeddedAllTextsExtracted: setEmbeddedAllTextsExtracted(bValue); break;

    case H_embeddedScenarioWidth: setEmbeddedScenarioWidth(value.toInt()); break;
    case H_embeddedTranslationWaitTime: setEmbeddedTranslationWaitTime(value.toInt()); break;

    case H_scenarioSignature: setScenarioSignature(value.toLong()); break;
    case H_nameSignature: setNameSignature(value.toLong()); break;

    case H_embeddedFontFamily: setEmbeddedFontFamily(value); break;
    case H_embeddedFontCharSet: setEmbeddedFontCharSet(value.toInt()); break;
    case H_embeddedFontCharSetEnabled: setEmbeddedFontCharSetEnabled(bValue); break;
    case H_embeddedFontWeight: setEmbeddedFontWeight(value.toInt()); break;
    case H_embeddedFontScale: setEmbeddedFontScale(value.toFloat()); break;
    case H_gameEncoding: setGameEncoding(value); break;

    case H_debug:
      if (bValue)
        Util::installDebugMsgHandler();
      else
        Util::uninstallDebugMsgHandler();
      break;
    default: DOUT("warning: unknown key:" << it.key());
    }
  }

  emit loadFinished();
}

// EOF
