// maindriver.cc
// 2/1/2013 jichi

#include "config.h"
#include "driver/maindriver.h"
#include "driver/maindriver_p.h"
#include "driver/rpcclient.h"
#include "driver/settings.h"
#include "embed/embeddriver.h"
#include "hijack/hijackdriver.h"
#include "hijack/hijackdriver.h"
#include "window/windowdriver.h"
#include "windbg/unload.h"

#define DEBUG "maindriver"
#include "sakurakit/skdebug.h"

/** Public class */

MainDriver::MainDriver(QObject *parent)
  : Base(parent), d_(new D(this))
{
  connect(this, SIGNAL(deleteLaterRequested()), SLOT(deleteLater()), Qt::QueuedConnection);
}

MainDriver::~MainDriver() { delete d_; }

void MainDriver::requestDeleteLater() { emit deleteLaterRequested(); }

void MainDriver::quit() { d_->quit(); }

/** Private class */

MainDriverPrivate::MainDriverPrivate(QObject *parent)
  : Base(parent), settings(nullptr), rpc(nullptr), hijack(nullptr), win(nullptr), eng(nullptr)
{
  DOUT("enter");
  settings = new Settings(this);
  {
    connect(settings, SIGNAL(loadFinished()), SLOT(onLoadFinished()));
  }

  rpc = new RpcClient(this);
  {
    //connect(rpc, SIGNAL(enableWindowTranslationRequested(bool)), settings, SLOT(setWindowTranslationEnabled(bool)));
    connect(rpc, SIGNAL(disconnected()), SLOT(onDisconnected()));
    connect(rpc, SIGNAL(detachRequested()), SLOT(unload()));
    //connect(rpc, SIGNAL(enabledRequested(bool)), settings, SLOT(setEnabled(bool)));
    connect(rpc, SIGNAL(settingsReceived(QString)), settings, SLOT(load(QString)));
    connect(rpc, SIGNAL(disableRequested()), settings, SLOT(disable()));
  }
  DOUT("leave");
}

void MainDriverPrivate::quit()
{
  if (eng)
    eng->quit();
  rpc->quit();
}

void MainDriverPrivate::createHijackDriver()
{
  if (hijack)
    return;
  hijack = new HijackDriver(this);
  hijack->setEncoding(settings->gameEncoding());
  hijack->setFontFamily(settings->embeddedFontFamily());
  hijack->setFontCharSet(settings->embeddedFontCharSet());
  hijack->setFontCharSetEnabled(settings->isEmbeddedFontCharSetEnabled());
  hijack->setFontScale(settings->embeddedFontScale());
  hijack->setFontWeight(settings->embeddedFontWeight());
  connect(settings, SIGNAL(gameEncodingChanged(QString)), hijack, SLOT(setEncoding(QString)));
  connect(settings, SIGNAL(embeddedFontFamilyChanged(QString)), hijack, SLOT(setFontFamily(QString)));
  connect(settings, SIGNAL(embeddedFontCharSetChanged(int)), hijack, SLOT(setFontCharSet(int)));
  connect(settings, SIGNAL(embeddedFontCharSetEnabledChanged(bool)), hijack, SLOT(setFontCharSetEnabled(bool)));
  connect(settings, SIGNAL(embeddedFontScaleChanged(float)), hijack, SLOT(setFontScale(float)));
  connect(settings, SIGNAL(embeddedFontWeightChanged(int)), hijack, SLOT(setFontWeight(int)));

  if (eng) {
    hijack->setDeviceContextFontEnabled(eng->isDeviceContextFontEnabled());
    hijack->setLocaleEmulationEnabled(eng->isLocaleEmulationEnabled());
  }
}

void MainDriverPrivate::createWindowDriver()
{
  if (win)
    return;

  win = new WindowDriver(this);

  win->setEncoding(settings->gameEncoding());
  win->setTextVisible(settings->isWindowTextVisible());
  win->setTranscodingEnabled(settings->isWindowTranscodingEnabled());
  win->setTranslationEnabled(settings->isWindowTranslationEnabled());

  connect(settings, SIGNAL(gameEncodingChanged(QString)), win, SLOT(setEncoding(QString)));
  connect(settings, SIGNAL(windowTextVisibleChanged(bool)), win, SLOT(setTextVisible(bool)));
  connect(settings, SIGNAL(windowTranscodingEnabledChanged(bool)), win, SLOT(setTranscodingEnabled(bool)));
  connect(settings, SIGNAL(windowTranslationEnabledChanged(bool)), win, SLOT(setTranslationEnabled(bool)));

  connect(win, SIGNAL(translationRequested(QString)), rpc, SLOT(requestWindowTranslation(QString)));
  connect(rpc, SIGNAL(clearTranslationRequested()), win, SLOT(clearTranslation()));
  connect(rpc, SIGNAL(windowTranslationReceived(QString)), win, SLOT(updateTranslation(QString)));

  win->setEnabled(settings->isWindowDriverNeeded()); // enable it at last
}

void MainDriverPrivate::createEmbedDriver()
{
  if (eng)
    return;

  eng = new EmbedDriver(this);

  // Use queued connection to quarantine the engine thrread
  connect(eng, SIGNAL(textReceived(QString,qint64,long,int,bool)), rpc, SLOT(sendEngineText(QString,qint64,long,int,bool)),
      Qt::QueuedConnection);
  //connect(eng, SIGNAL(textReceivedDelayed(QString,qint64,int,bool)), rpc, SLOT(sendEngineTextLater(QString,qint64,int,bool)),
  //    Qt::QueuedConnection);
  connect(eng, SIGNAL(engineNameChanged(QString)), rpc, SLOT(sendEngineName(QString)));
  connect(rpc, SIGNAL(clearTranslationRequested()), eng, SLOT(clearTranslation()));
  //connect(rpc, SIGNAL(enableEngineRequested(bool)), eng, SLOT(setEnable(bool)));
  //connect(rpc, SIGNAL(engineTranslationReceived(QString,qint64,int,QString)), eng, SLOT(updateTranslation(QString,qint64,int,QString)));

  connect(rpc, SIGNAL(reconnected()), eng, SLOT(sendEngineName()));

  connect(settings, SIGNAL(embeddedScenarioVisibleChanged(bool)), eng, SLOT(setScenarioVisible(bool)));
  connect(settings, SIGNAL(embeddedScenarioTextVisibleChanged(bool)), eng, SLOT(setScenarioTextVisible(bool)));
  connect(settings, SIGNAL(embeddedScenarioTranscodingEnabledChanged(bool)), eng, SLOT(setScenarioTranscodingEnabled(bool)));
  connect(settings, SIGNAL(embeddedScenarioTranslationEnabledChanged(bool)), eng, SLOT(setScenarioTranslationEnabled(bool)));
  connect(settings, SIGNAL(embeddedNameVisibleChanged(bool)), eng, SLOT(setNameVisible(bool)));
  connect(settings, SIGNAL(embeddedNameTextVisibleChanged(bool)), eng, SLOT(setNameTextVisible(bool)));
  connect(settings, SIGNAL(embeddedNameTranscodingEnabledChanged(bool)), eng, SLOT(setNameTranscodingEnabled(bool)));
  connect(settings, SIGNAL(embeddedNameTranslationEnabledChanged(bool)), eng, SLOT(setNameTranslationEnabled(bool)));
  connect(settings, SIGNAL(embeddedOtherVisibleChanged(bool)), eng, SLOT(setOtherVisible(bool)));
  connect(settings, SIGNAL(embeddedOtherTextVisibleChanged(bool)), eng, SLOT(setOtherTextVisible(bool)));
  connect(settings, SIGNAL(embeddedOtherTranscodingEnabledChanged(bool)), eng, SLOT(setOtherTranscodingEnabled(bool)));
  connect(settings, SIGNAL(embeddedOtherTranslationEnabledChanged(bool)), eng, SLOT(setOtherTranslationEnabled(bool)));

  connect(settings, SIGNAL(embeddedTextEnabledChanged(bool)), eng, SLOT(setEnabled(bool)));

  connect(settings, SIGNAL(embeddedScenarioWidthChanged(int)), eng, SLOT(setScenarioWidth(int)));

  connect(settings, SIGNAL(embeddedSpaceAlwaysInsertedChanged(bool)), eng, SLOT(setAlwaysInsertsSpaces(bool)));
  connect(settings, SIGNAL(embeddedSpaceSmartInsertedChanged(bool)), eng, SLOT(setSmartInsertsSpaces(bool)));
  connect(settings, SIGNAL(embeddedSpacePolicyEncodingChanged(QString)), eng, SLOT(setSpacePolicyEncoding(QString)));

  //connect(settings, SIGNAL(embeddedTextCancellableByControlChanged(bool)), eng, SLOT(setDetectsControl(bool)));
  connect(settings, SIGNAL(embeddedAllTextsExtractedChanged(bool)), eng, SLOT(setExtractsAllTexts(bool)));

  connect(settings, SIGNAL(scenarioSignatureChanged(long)), eng, SLOT(setScenarioSignature(long)));
  connect(settings, SIGNAL(nameSignatureChanged(long)), eng, SLOT(setNameSignature(long)));

  connect(settings, SIGNAL(embeddedTranslationWaitTimeChanged(int)), eng, SLOT(setTranslationWaitTime(int)));
  eng->setTranslationWaitTime(settings->embeddedTranslationWaitTime());

  connect(settings, SIGNAL(gameEncodingChanged(QString)), eng, SLOT(setEncoding(QString)));

  if (eng->load()) {
    eng->setEncoding(settings->gameEncoding());

    eng->setScenarioVisible(settings->isEmbeddedScenarioVisible());
    eng->setScenarioTextVisible(settings->isEmbeddedScenarioTextVisible());
    eng->setScenarioTranscodingEnabled(settings->isEmbeddedScenarioTranscodingEnabled());
    eng->setScenarioTranslationEnabled(settings->isEmbeddedScenarioTranslationEnabled());
    eng->setNameVisible(settings->isEmbeddedNameVisible());
    eng->setNameTextVisible(settings->isEmbeddedNameTextVisible());
    eng->setNameTranscodingEnabled(settings->isEmbeddedNameTranscodingEnabled());
    eng->setNameTranslationEnabled(settings->isEmbeddedNameTranslationEnabled());
    eng->setOtherVisible(settings->isEmbeddedOtherVisible());
    eng->setOtherTextVisible(settings->isEmbeddedOtherTextVisible());
    eng->setOtherTranscodingEnabled(settings->isEmbeddedOtherTranscodingEnabled());
    eng->setOtherTranslationEnabled(settings->isEmbeddedOtherTranslationEnabled());

    eng->setAlwaysInsertsSpaces(settings->isEmbeddedSpaceAlwaysInserted());
    eng->setSmartInsertsSpaces(settings->isEmbeddedSpaceSmartInserted());
    eng->setSpacePolicyEncoding(settings->embeddedSpacePolicyEncoding());

    eng->setScenarioWidth(settings->embeddedScenarioWidth());

    //eng->setDetectsControl(settings->isEmbeddedTextCancellableByControl());
    eng->setExtractsAllTexts(settings->isEmbeddedAllTextsExtracted());

    eng->setScenarioSignature(settings->scenarioSignature());
    eng->setNameSignature(settings->nameSignature());

    // Always enable text extraction
    eng->setScenarioExtractionEnabled(true);
    eng->setNameExtractionEnabled(true);
  }
  //eng->setEnabled(settings->isEmbedDriverNeeded()); // enable it at last
  eng->setEnabled(settings->isEmbeddedTextEnabled());
}

void MainDriverPrivate::onDisconnected()
{
  if (win)
    win->setEnabled(false);
  //DOUT("pass");
  unload();
}

void MainDriverPrivate::unload()
{
#ifdef VNRAGENT_ENABLE_UNLOAD
  // Add contents to qDebug will crash the application while unload.
  //DOUT("enter");
  if (hijack) hijack->unload();
  if (eng) eng->unload();
  //DOUT("leave");
  WinDbg::unloadCurrentModule();
#endif // VNRAGENT_ENABLE_UNLOAD
}

void MainDriverPrivate::onLoadFinished()
{
  if (eng)
    ; //eng->setEnabled(settings->isEmbedDriverNeeded());
  else if (settings->isEmbedDriverNeeded()){
    createEmbedDriver();
    createHijackDriver();
  }
  if (win)
    win->setEnabled(settings->isWindowDriverNeeded());
  else if (settings->isWindowDriverNeeded()){
    createWindowDriver();
    createHijackDriver();
  }
}

// EOF
