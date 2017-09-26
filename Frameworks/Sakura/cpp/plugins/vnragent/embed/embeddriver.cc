// embeddriver.cc
// 4/26/2014 jichi

#include "embed/embeddriver.h"
#include "embed/embedmanager.h"
#include "engine/enginecontroller.h"
#include "engine/enginemodel.h"
#include "engine/enginefactory.h"
#include "engine/enginesettings.h"

/** Private class */

class EmbedDriverPrivate
{
public:
  EmbedManager *manager;
  EngineController *engine;

  explicit EmbedDriverPrivate(QObject *parent)
    : manager(new EmbedManager(parent)), engine(nullptr) {}

  ~EmbedDriverPrivate() { if (engine) delete engine; }
};

/** Public class */

//static EmbedDriver *instance_;
//EmbedDriver *EmbedDriver::instance() { return instance_; }

EmbedDriver::EmbedDriver(QObject *parent)
  : Base(parent), d_(new D(this))
{
  connect(d_->manager, SIGNAL(textReceived(QString,qint64,long,int,bool)), SIGNAL(textReceived(QString,qint64,long,int,bool)));
}

EmbedDriver::~EmbedDriver()
{
  //::instance_ = nullptr;
  delete d_;
}

// - Properties -

bool EmbedDriver::isDeviceContextFontEnabled() const { return  d_->engine && d_->engine->model()->enableDynamicFont; }
bool EmbedDriver::isLocaleEmulationEnabled() const { return  d_->engine && d_->engine->model()->enableLocaleEmulation; }

void EmbedDriver::setTranslationWaitTime(int v)  { d_->manager->setTranslationWaitTime(v); }

void EmbedDriver::setEncoding(const QString &v)  { if (d_->engine) d_->engine->setEncoding(v); }

void EmbedDriver::setEnabled(bool t)  { if (d_->engine) d_->engine->settings()->enabled = t; }
//void EmbedDriver::setDetectsControl(bool t) { if (d_->engine) d_->engine->settings()->detectsControl = t; }
void EmbedDriver::setExtractsAllTexts(bool t) { if (d_->engine) d_->engine->settings()->extractsAllTexts = t; }

void EmbedDriver::setAlwaysInsertsSpaces(bool t) { if (d_->engine) d_->engine->settings()->alwaysInsertsSpaces = t; }
void EmbedDriver::setSmartInsertsSpaces(bool t) { if (d_->engine) d_->engine->settings()->smartInsertsSpaces = t; }
void EmbedDriver::setSpacePolicyEncoding(const QString &v) { if (d_->engine) d_->engine->setSpacePolicyEncoding(v); }

void EmbedDriver::setScenarioWidth(int v) { if (d_->engine) d_->engine->settings()->scenarioWidth = v; }

void EmbedDriver::setScenarioSignature(long v) { if (d_->engine) d_->engine->settings()->scenarioSignature = v; }
void EmbedDriver::setNameSignature(long v) { if (d_->engine) d_->engine->settings()->nameSignature = v; }

void EmbedDriver::setScenarioVisible(bool t) { if (d_->engine) d_->engine->settings()->textVisible[Engine::ScenarioRole] = t; }
void EmbedDriver::setScenarioTextVisible(bool t) { if (d_->engine) d_->engine->settings()->scenarioTextVisible = t; }
void EmbedDriver::setScenarioExtractionEnabled(bool t) { if (d_->engine) d_->engine->settings()->extractionEnabled[Engine::ScenarioRole] = t; }
void EmbedDriver::setScenarioTranscodingEnabled(bool t) { if (d_->engine) d_->engine->settings()->transcodingEnabled[Engine::ScenarioRole] = t; }
void EmbedDriver::setScenarioTranslationEnabled(bool t) { if (d_->engine) d_->engine->settings()->translationEnabled[Engine::ScenarioRole] = t; }
void EmbedDriver::setNameVisible(bool t) { if (d_->engine) d_->engine->settings()->textVisible[Engine::NameRole] = t; }
void EmbedDriver::setNameTextVisible(bool t) { if (d_->engine) d_->engine->settings()->nameTextVisible = t; }
void EmbedDriver::setNameExtractionEnabled(bool t) { if (d_->engine) d_->engine->settings()->extractionEnabled[Engine::NameRole] = t; }
void EmbedDriver::setNameTranscodingEnabled(bool t) { if (d_->engine) d_->engine->settings()->transcodingEnabled[Engine::NameRole] = t; }
void EmbedDriver::setNameTranslationEnabled(bool t) { if (d_->engine) d_->engine->settings()->translationEnabled[Engine::NameRole] = t; }
void EmbedDriver::setOtherVisible(bool t) { if (d_->engine) d_->engine->settings()->textVisible[Engine::OtherRole] = t; }
void EmbedDriver::setOtherTextVisible(bool t) { if (d_->engine) d_->engine->settings()->otherTextVisible = t; }
void EmbedDriver::setOtherExtractionEnabled(bool t) { if (d_->engine) d_->engine->settings()->extractionEnabled[Engine::OtherRole] = t; }
void EmbedDriver::setOtherTranscodingEnabled(bool t) { if (d_->engine) d_->engine->settings()->transcodingEnabled[Engine::OtherRole] = t; }
void EmbedDriver::setOtherTranslationEnabled(bool t) { if (d_->engine) d_->engine->settings()->translationEnabled[Engine::OtherRole] = t; }

// - Actions -

QString EmbedDriver::engineName() const
{ return d_->engine ? d_->engine->name() : QString(); }

void EmbedDriver::sendEngineName()
{ emit engineNameChanged(engineName()); }

bool EmbedDriver::load()
{
  d_->engine = EngineFactory::createEngine();
  sendEngineName();
  return d_->engine;
}

void EmbedDriver::clearTranslation()  { d_->manager->clearTranslation(); }

//void EmbedDriver::updateTranslation(const QString &text, qint64 hash, int role)
//{ d_->manager->updateTranslation(text, hash, role); }

void EmbedDriver::quit()
{ d_->manager->quit(); }

void EmbedDriver::unload()
{
  if (d_->engine)
    d_->engine->unload();
}

// EOF
