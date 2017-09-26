// embedmanager.cc
// 4/26/2014 jichi

#include "config.h"
#include "embed/embedmanager.h"
#include "embed/embedmemory.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/engineutil.h"
#include "driver/rpcclient.h"
//#include "QxtCore/QxtJSON"
//#include "qtjson/qtjson.h"
#include "winevent/winevent.h"
#include "winmutex/winmutex.h"
#include <QtCore/QCoreApplication>
#include <QtCore/QHash>
#include <QtCore/QStringList>
#include <qt_windows.h>
//#include "debug.h"

//#define ENGINE_SLEEP_EVENT "vnragent_engine_sleep"
#define D_LOCK win_mutex_lock<D::mutex_type> d_lock(d_->mutex)

// TODO: Use read-write lock instead
//#define D_LOCK (void)0 // locking is temporarily disabled to avoid hanging

#define DEBUG "embedmanager"
#include "sakurakit/skdebug.h"

/** Private class */

class EmbedManagerPrivate
{
public:
  struct TextEntry
  {
    QString text,
            language;
    TextEntry() {}
    TextEntry(const QString &text, const QString &language) : text(text), language(language) {}
    explicit TextEntry(const QString &text) : text(text) {}
  };
  QHash<qint64, TextEntry> translations;   // cached, {key:text}

  typedef win_mutex<CRITICAL_SECTION> mutex_type;
  mutex_type mutex; // mutex to lock translations

  int waitTime;

  EmbedMemory *memory;

  EmbedManagerPrivate(QObject *parent)
    : waitTime(1000) // sleep for 1 second by default
    , memory(new EmbedMemory(parent))
  {
    memory->create();
  }

  static inline QString createEventName(qint64 hash, int role)
  {
    qint64 pid = QCoreApplication::applicationPid();
    return QString(VNRAGENT_MEMORY_EVENT)
      .arg(QString::number(pid), QString::number(role), QString::number(hash))
      .replace('-', '_') // get rid of minus sign
    ;
  }

  //static void sleep(int msecs) { ::Sleep(msecs); }
  //void notify() {}
};

//  // - Event -
//  // Sleep 10*100 = 1 second
//  enum { SleepTimeout = 100 };
//  enum { SleepCount = 10 };
//  void sleep(int interval = SleepTimeout, int count = SleepCount)
//  {
//    sleepEvent.signal(false);
//    for (int i = 0; !sleepEvent.wait(interval) && i < count; i++);
//    //sleepEvent.signal(false);
//  }
//
//  void notify() { sleepEvent.signal(true); }

//  mutex_type sleepMutex;
//  typedef win_mutex_cond<CONDITION_VARIABLE> cond_type;
//  cond_type sleepCond;
//  void sleep()
//  {
//    sleepMutex.lock();
//    sleepCond.wait_for(sleepMutex, SleepTimeout * SleepCount);
//  }
//  void notify() { sleepCond.notify_all(); }

/** Public class */

// - Construction -

static EmbedManager *instance_;
EmbedManager *EmbedManager::instance() { return instance_; }

EmbedManager::EmbedManager(QObject *parent)
  : Base(parent), d_(new D(this))
{ ::instance_ = this; }

EmbedManager::~EmbedManager()
{
  ::instance_ = nullptr;
  delete d_;
}

void EmbedManager::setTranslationWaitTime(int msecs)
{ d_->waitTime = msecs; }

//bool EmbedManager::tryLock() { return d_->mutex.try_lock(); }
//void EmbedManager::lock() { d_->mutex.lock(); }
//void EmbedManager::unlock() { d_->mutex.unlock(); }


// - Actions -

void EmbedManager::quit()
{
  D_LOCK;
  if (d_->memory->isAttached())
    d_->memory->detach();
}

void EmbedManager::clearTranslation()
{
  D_LOCK;
  d_->translations.clear();
}

//void EmbedManager::updateTranslation(const QString &text, qint64 hash, int role)
//{
//  D_LOCK;
//  qint64 key = Engine::hashTextKey(hash, role);
//  d_->translations[key] = text;
//  //d_->notify();
//}

//void EmbedManager::abortTranslation()
//{ d_->unblock(); }

void EmbedManager::sendText(const QString &text, qint64 hash, long signature, int role, bool needsTranslation)
{
#ifdef VNRAGENT_ENABLE_NATIVE_PIPE
  if (needsTranslation)
    RpcClient::instance()->directSendEngineText(text, hash, signature, role, needsTranslation);
  else
#endif // VNRAGENT_ENABLE_NATIVE_PIPE
  emit textReceived(text, hash, signature, role, needsTranslation);
}

QString EmbedManager::findTranslation(qint64 hash, int role, QString *language) const
{
  D_LOCK;
  if (role <= 1) {
    qint64 key = Engine::hashTextKey(hash, role);
    auto p = d_->translations.constFind(key);
    if (p != d_->translations.constEnd()) {
      const auto &v = p.value();
      if (language)
        *language = v.language;
      return v.text;
    }
  } else {
    QString ret;
    for (int i = role; i > 0; i--) {
      qint64 key = Engine::hashTextKey(hash, i);
      auto p = d_->translations.constFind(key);
      if (p != d_->translations.constEnd()) {
        const auto &v = p.value();
        if (language)
          *language = v.language;
        return v.text;
      }
    }
  }
  return QString();
}

QString EmbedManager::waitForTranslation(qint64 hash, int role, QString *language) const
{
  qint64 key = Engine::hashTextKey(hash, role);
  {
    D_LOCK;
    auto p = d_->translations.constFind(key);
    if (p != d_->translations.constEnd()) {
      const auto &v = p.value();
      if (language)
        *language = v.language;
      return v.text;
    }
  }

  QString ret;
  auto m = d_->memory;
  if (ret.isEmpty() && m->isAttached()) {
    QString eventName = D::createEventName(hash, role);
    win_event event(eventName.toAscii());
    enum { WaitInterval = VNRAGENT_MEMORY_TIMEOUT };
    //int WaitInterval = d_->waitTime;
    int waitCount = qMax(1, d_->waitTime / WaitInterval);

    for (int count = 0;
        count <= waitCount && m->isAttached() && !Engine::isPauseKeyPressed();
        count++) { // repeat twice
      for (int i = 0; i < m->cellCount(); i++)
        if (m->dataRole(i) == role && m->dataHash(i) == hash) {
          if (m->isDataCanceled(i))
            return ret;
          if (m->isDataReady(i)) {
            QString lang = m->dataLanguage(i);
            if (language)
              *language = lang;
            ret = d_->memory->dataText(i);
            if (!ret.isEmpty()) {
              D_LOCK;
              d_->translations[key] = D::TextEntry(ret, lang);
            }
            return ret;
          }
        }
      if (count != waitCount) {
        if (event.wait(WaitInterval)) // if wake up by VNR, no longer wait anymore
          count = waitCount - 1;
      }
    }
  }
  return ret;
}

// EOF
